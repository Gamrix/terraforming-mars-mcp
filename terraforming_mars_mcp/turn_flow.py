from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request

from .api_response_models import (
    GameLogEntryModel as ApiGameLogEntryModel,
    PlayerViewModel as ApiPlayerViewModel,
    WaitingForStatusModel as ApiWaitingForStatusModel,
)
from .game_state import _build_agent_state
from .waiting_for import _get_waiting_for_model

TURN_WAIT_TIMEOUT_SECONDS = 2 * 60 * 60
TURN_WAIT_POLL_INTERVAL_SECONDS = 2
# TM-OSS serializes LogMessageDataType.PLAYER as numeric enum value 2.
PLAYER_LOG_DATA_TYPE_NUMERIC = 2


@dataclass
class SessionConfig:
    base_url: str = os.environ.get("TM_SERVER_URL", "http://localhost:8080")
    player_id: str | None = os.environ.get("TM_PLAYER_ID")


CFG = SessionConfig()


def _strip_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def _ensure_player_id(player_id: str | None = None) -> str:
    pid = player_id or CFG.player_id
    if not pid:
        raise ValueError("player_id is not set. Call configure_session first.")
    return pid


def _http_json(
    method: str,
    path: str,
    query: dict[str, str] | None = None,
    body: Any | None = None,
) -> Any:
    url = _strip_base_url(CFG.base_url) + path
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
            return json.loads(raw)
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


def _normalize_player_view(
    player_model: ApiPlayerViewModel | dict[str, object],
) -> ApiPlayerViewModel:
    if isinstance(player_model, ApiPlayerViewModel):
        return player_model
    return ApiPlayerViewModel.model_validate(player_model)


def _normalize_log_entry(
    entry: ApiGameLogEntryModel | dict[str, object],
) -> ApiGameLogEntryModel:
    if isinstance(entry, ApiGameLogEntryModel):
        return entry
    return ApiGameLogEntryModel.model_validate(entry)


def _get_player(player_id: str | None = None) -> ApiPlayerViewModel:
    pid = _ensure_player_id(player_id)
    result = _http_json("GET", "/api/player", {"id": pid})
    if not isinstance(result, dict):
        raise RuntimeError("Unexpected /api/player response")
    return ApiPlayerViewModel.model_validate(result)


def _post_input(
    response: dict[str, object], player_id: str | None = None
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


def _has_waiting_input(player_model: ApiPlayerViewModel | dict[str, object]) -> bool:
    return _get_waiting_for_model(player_model) is not None


def _log_signature(entry: ApiGameLogEntryModel | dict[str, object]) -> str:
    parsed_entry = _normalize_log_entry(entry)
    return json.dumps(
        {
            "timestamp": parsed_entry.timestamp,
            "message": parsed_entry.message,
            "data": parsed_entry.data,
            "type": parsed_entry.type,
            "playerId": parsed_entry.playerId,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _build_color_name_map(
    player_model: ApiPlayerViewModel | dict[str, object],
) -> dict[str, str]:
    parsed_player = _normalize_player_view(player_model)
    mapping: dict[str, str] = {}
    for player in parsed_player.players:
        color = player.color
        name = player.name
        if color and name:
            mapping[color] = name
    return mapping


def _format_log_entry(
    entry: ApiGameLogEntryModel | dict[str, object], color_to_name: dict[str, str]
) -> str:
    parsed_entry = _normalize_log_entry(entry)
    template = parsed_entry.message
    data = parsed_entry.data
    if not isinstance(data, list):
        return str(template)

    def replace(match: re.Match[str]) -> str:
        idx = int(match.group(1))
        if idx < 0 or idx >= len(data):
            return match.group(0)
        datum = data[idx]
        if not isinstance(datum, dict):
            return match.group(0)
        value = datum.get("value")
        data_type = datum.get("type")
        if _is_player_log_data_type(data_type) and isinstance(value, str):
            return color_to_name.get(value, value)
        if value is None:
            return ""
        return str(value)

    return re.sub(r"\$\{(\d{1,2})\}", replace, template)


def _extract_opponent_actions(
    initial_logs: list[ApiGameLogEntryModel | dict[str, object]],
    final_logs: list[ApiGameLogEntryModel | dict[str, object]],
    opponent_colors: set[str],
    color_to_name: dict[str, str],
) -> list[str]:
    seen = {_log_signature(entry) for entry in initial_logs}
    actions: list[str] = []
    for entry in final_logs:
        parsed_entry = _normalize_log_entry(entry)
        signature = _log_signature(entry)
        if signature in seen:
            continue
        data = parsed_entry.data
        if not isinstance(data, list):
            continue
        has_opponent = False
        for datum in data:
            if not isinstance(datum, dict):
                continue
            if _is_player_log_data_type(datum.get("type")) and datum.get(
                "value"
            ) in opponent_colors:
                has_opponent = True
                break
        if has_opponent:
            actions.append(_format_log_entry(parsed_entry, color_to_name))
    return actions


def _is_player_log_data_type(data_type: Any) -> bool:
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
    player_model: ApiPlayerViewModel | dict[str, object],
    initial_logs: list[ApiGameLogEntryModel | dict[str, object]] | None = None,
) -> tuple[ApiPlayerViewModel, list[str]]:
    parsed_player = _normalize_player_view(player_model)
    game = parsed_player.game

    this_color = parsed_player.thisPlayer.color
    color_to_name = _build_color_name_map(parsed_player)
    opponent_colors = {color for color in color_to_name if color != this_color}
    start_logs = initial_logs if initial_logs is not None else _get_game_logs()

    game_age = int(game.gameAge)
    undo_count = int(game.undoCount)
    deadline = time.monotonic() + TURN_WAIT_TIMEOUT_SECONDS
    last_waitingfor: dict[str, object] | None = None

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
            if _has_waiting_input(refreshed):
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


def _submit_and_return_state(response: dict[str, object]) -> dict[str, object]:
    player_model = _post_input(response)
    if not _has_waiting_input(player_model):
        initial_logs = _get_game_logs()
        refreshed, opponent_actions = _wait_for_turn_from_player_model(
            player_model, initial_logs=initial_logs
        )
        result = _build_agent_state(
            refreshed, base_url=CFG.base_url, player_id_fallback=CFG.player_id
        )
        if opponent_actions:
            result["opponent_actions_between_turns"] = opponent_actions
        return result
    return _build_agent_state(
        player_model, base_url=CFG.base_url, player_id_fallback=CFG.player_id
    )
