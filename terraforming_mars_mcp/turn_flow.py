from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Mapping, Sequence, cast
from urllib import error, parse, request

from .api_response_models import (
    GameLogEntryModel as ApiGameLogEntryModel,
    JsonValue,
    PlayerViewModel as ApiPlayerViewModel,
    WaitingForStatusModel as ApiWaitingForStatusModel,
)
from .game_state import _build_agent_state

TURN_WAIT_TIMEOUT_SECONDS = 2 * 60 * 60
TURN_WAIT_POLL_INTERVAL_SECONDS = 2
# TM-OSS serializes LogMessageDataType.PLAYER as numeric enum value 2.
PLAYER_LOG_DATA_TYPE_NUMERIC = 2


@dataclass
class SessionConfig:
    base_url: str = os.environ.get("TM_SERVER_URL", "http://localhost:8080")
    player_id: str | None = os.environ.get("TM_PLAYER_ID")


CFG = SessionConfig()


def _ensure_player_id(player_id: str | None = None) -> str:
    pid = player_id or CFG.player_id
    if not pid:
        raise ValueError("player_id is not set. Call configure_session first.")
    return pid


def _http_json(
    method: str,
    path: str,
    query: Mapping[str, str] | None = None,
    body: JsonValue | None = None,
) -> JsonValue:
    url = CFG.base_url.rstrip("/") + path
    if query:
        url += "?" + parse.urlencode(query)

    payload = None
    headers: dict[str, str] = {}
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url=url, data=payload, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            if not raw:
                return {}
            return cast(JsonValue, json.loads(raw))
    except error.HTTPError as exc:
        raw_error = exc.read().decode("utf-8", errors="replace")
        message = raw_error
        try:
            parsed_json = json.loads(raw_error)
            if isinstance(parsed_json, dict) and "message" in parsed_json:
                message = str(parsed_json["message"])
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"HTTP {exc.code} {method} {path}: {message}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Cannot reach server at {CFG.base_url}: {exc}") from exc


def _get_player(player_id: str | None = None) -> ApiPlayerViewModel:
    pid = _ensure_player_id(player_id)
    result = _http_json("GET", "/api/player", {"id": pid})
    if not isinstance(result, dict):
        raise RuntimeError("Unexpected /api/player response")
    return ApiPlayerViewModel.model_validate(result)


def _post_input(
    response: dict[str, JsonValue], player_id: str | None = None
) -> ApiPlayerViewModel:
    pid = _ensure_player_id(player_id)
    result = _http_json("POST", "/player/input", {"id": pid}, response)
    if not isinstance(result, dict):
        raise RuntimeError("Unexpected /player/input response")
    return ApiPlayerViewModel.model_validate(result)


def _get_waiting_for_state(
    game_age: int, undo_count: int, player_id: str | None = None
) -> ApiWaitingForStatusModel:
    pid = _ensure_player_id(player_id)
    result = _http_json(
        "GET",
        "/api/waitingfor",
        {"id": pid, "gameAge": str(game_age), "undoCount": str(undo_count)},
    )
    if not isinstance(result, dict):
        raise RuntimeError("Unexpected /api/waitingfor response")
    return ApiWaitingForStatusModel.model_validate(result)


def _get_game_logs(player_id: str | None = None) -> list[ApiGameLogEntryModel]:
    pid = _ensure_player_id(player_id)
    result = _http_json("GET", "/api/game/logs", {"id": pid})
    if not isinstance(result, list):
        raise RuntimeError("Unexpected /api/game/logs response")
    normalized_logs: list[ApiGameLogEntryModel] = []
    for item in result:
        if not isinstance(item, dict):
            continue
        normalized_logs.append(ApiGameLogEntryModel.model_validate(item))
    return normalized_logs


def _log_signature(entry: ApiGameLogEntryModel) -> str:
    return json.dumps(
        {
            "timestamp": entry.timestamp,
            "message": entry.message,
            "data": [datum.model_dump(exclude_none=True) for datum in entry.data],
            "type": entry.type,
            "playerId": entry.playerId,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _build_color_name_map(player_model: ApiPlayerViewModel) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for player in player_model.players:
        color = player.color
        name = player.name
        if color and name:
            mapping[color] = name
    return mapping


def _format_log_entry(
    entry: ApiGameLogEntryModel, color_to_name: dict[str, str]
) -> str:
    template = entry.message
    data = entry.data

    def replace(match: re.Match[str]) -> str:
        idx = int(match.group(1))
        if idx < 0 or idx >= len(data):
            return match.group(0)
        datum = data[idx]
        value = datum.value
        data_type = datum.type
        if _is_player_log_data_type(data_type) and isinstance(value, str):
            return color_to_name.get(value, value)
        if value is None:
            return ""
        return str(value)

    return re.sub(r"\$\{(\d{1,2})\}", replace, template)


def _extract_opponent_actions(
    initial_logs: Sequence[ApiGameLogEntryModel],
    final_logs: Sequence[ApiGameLogEntryModel],
    opponent_colors: set[str],
    color_to_name: dict[str, str],
) -> list[str]:
    seen = {_log_signature(entry) for entry in initial_logs}
    actions: list[str] = []
    for entry in final_logs:
        signature = _log_signature(entry)
        if signature in seen:
            continue
        data = entry.data
        has_opponent = False
        for datum in data:
            if _is_player_log_data_type(datum.type) and datum.value in opponent_colors:
                has_opponent = True
                break
        if has_opponent:
            actions.append(_format_log_entry(entry, color_to_name))
    return actions


def _is_player_log_data_type(data_type: int | str | None) -> bool:
    if isinstance(data_type, int):
        return data_type == PLAYER_LOG_DATA_TYPE_NUMERIC
    if isinstance(data_type, str):
        lowered = data_type.strip().lower()
        if lowered == "player":
            return True
        if lowered.isdigit():
            return int(lowered) == PLAYER_LOG_DATA_TYPE_NUMERIC
    return False


def _wait_for_turn_from_player_model(
    player_model: ApiPlayerViewModel,
    initial_logs: Sequence[ApiGameLogEntryModel] | None = None,
) -> tuple[ApiPlayerViewModel, list[str]]:
    game = player_model.game

    this_color = player_model.thisPlayer.color
    color_to_name = _build_color_name_map(player_model)
    opponent_colors = {color for color in color_to_name if color != this_color}
    start_logs = (
        list(initial_logs) if initial_logs is not None else _get_game_logs()
    )

    game_age = int(game.gameAge)
    undo_count = int(game.undoCount)
    deadline = time.monotonic() + TURN_WAIT_TIMEOUT_SECONDS
    last_waitingfor: dict[str, JsonValue] | None = None

    while True:
        waiting = _get_waiting_for_state(game_age, undo_count)
        last_waitingfor = waiting.model_dump(exclude_none=True)
        status = waiting.result
        if status == "GO":
            refreshed = _get_player()
            final_logs = _get_game_logs()
            opponent_actions = _extract_opponent_actions(
                start_logs,
                final_logs,
                opponent_colors,
                color_to_name,
            )
            return refreshed, opponent_actions
        if status == "REFRESH":
            refreshed = _get_player()
            refreshed_game = refreshed.game
            game_age = int(refreshed_game.gameAge)
            undo_count = int(refreshed_game.undoCount)
            if refreshed.waitingFor is not None:
                final_logs = _get_game_logs()
                opponent_actions = _extract_opponent_actions(
                    start_logs,
                    final_logs,
                    opponent_colors,
                    color_to_name,
                )
                return refreshed, opponent_actions

        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Timed out waiting for turn after {TURN_WAIT_TIMEOUT_SECONDS} seconds. "
                f"Last waitingfor={last_waitingfor}"
            )
        time.sleep(TURN_WAIT_POLL_INTERVAL_SECONDS)


def _submit_and_return_state(response: Mapping[str, object]) -> dict[str, object]:
    player_model = _post_input(cast(dict[str, JsonValue], dict(response)))
    if player_model.waitingFor is None:
        initial_logs = _get_game_logs()
        refreshed, opponent_actions = _wait_for_turn_from_player_model(
            player_model, initial_logs=initial_logs
        )
        result = _build_agent_state(
            refreshed,
            base_url=CFG.base_url,
            player_id_fallback=CFG.player_id,
            auto_response=True,
        )
        if opponent_actions:
            result["opponent_actions_between_turns"] = opponent_actions
        return result
    return _build_agent_state(
        player_model,
        base_url=CFG.base_url,
        player_id_fallback=CFG.player_id,
        auto_response=True,
    )
