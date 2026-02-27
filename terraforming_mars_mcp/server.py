#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp",
#   "pydantic",
# ]
# ///

"""MCP server for playing Terraforming Mars via this repo's HTTP server."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import tempfile
import time
from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal
from urllib import error, parse, request

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

try:
    from .api_response_models import (
        CardModel as ApiCardModel,
        ClaimedMilestoneModel as ApiClaimedMilestoneModel,
        FundedAwardModel as ApiFundedAwardModel,
        GameLogEntryModel as ApiGameLogEntryModel,
        PlayerViewModel as ApiPlayerViewModel,
        PublicPlayerModel as ApiPublicPlayerModel,
        SpaceModel as ApiSpaceModel,
        WaitingForInputModel as ApiWaitingForInputModel,
        WaitingForStatusModel as ApiWaitingForStatusModel,
    )
except ImportError:
    from api_response_models import (  # type: ignore[no-redef]
        CardModel as ApiCardModel,
        ClaimedMilestoneModel as ApiClaimedMilestoneModel,
        FundedAwardModel as ApiFundedAwardModel,
        GameLogEntryModel as ApiGameLogEntryModel,
        PlayerViewModel as ApiPlayerViewModel,
        PublicPlayerModel as ApiPublicPlayerModel,
        SpaceModel as ApiSpaceModel,
        WaitingForInputModel as ApiWaitingForInputModel,
        WaitingForStatusModel as ApiWaitingForStatusModel,
    )


class InputType(StrEnum):
    AND_OPTIONS = "and"
    OR_OPTIONS = "or"
    SELECT_AMOUNT = "amount"
    SELECT_CARD = "card"
    SELECT_DELEGATE = "delegate"
    SELECT_PAYMENT = "payment"
    SELECT_PROJECT_CARD_TO_PLAY = "projectCard"
    SELECT_INITIAL_CARDS = "initialCards"
    SELECT_OPTION = "option"
    SELECT_PARTY = "party"
    SELECT_PLAYER = "player"
    SELECT_SPACE = "space"
    SELECT_COLONY = "colony"
    SELECT_PRODUCTION_TO_LOSE = "productionToLose"
    SHIFT_ARES_GLOBAL_PARAMETERS = "aresGlobalParameters"
    SELECT_GLOBAL_EVENT = "globalEvent"
    SELECT_POLICY = "policy"
    SELECT_RESOURCE = "resource"
    SELECT_RESOURCES = "resources"
    SELECT_CLAIMED_UNDERGROUND_TOKEN = "claimedUndergroundToken"


class ToolName(StrEnum):
    SUBMIT_RAW_ENTITY = "submit_raw_entity"
    CHOOSE_OR_OPTION = "choose_or_option"
    SUBMIT_AND_OPTIONS = "submit_and_options"
    SELECT_AMOUNT = "select_amount"
    SELECT_CARDS = "select_cards"
    SELECT_DELEGATE_TARGET = "select_delegate_target"
    PAY_FOR_ACTION = "pay_for_action"
    PAY_FOR_PROJECT_CARD = "pay_for_project_card"
    SELECT_INITIAL_CARDS = "select_initial_cards"
    CONFIRM_OPTION = "confirm_option"
    SELECT_PARTY = "select_party"
    SELECT_PLAYER = "select_player"
    SELECT_SPACE = "select_space"
    SELECT_COLONY = "select_colony"
    SELECT_PRODUCTION_TO_LOSE = "select_production_to_lose"
    SHIFT_ARES_GLOBAL_PARAMETERS = "shift_ares_global_parameters"
    SELECT_GLOBAL_EVENT = "select_global_event"
    SELECT_POLICY = "select_policy"
    SELECT_RESOURCE = "select_resource"
    SELECT_RESOURCES = "select_resources"
    SELECT_CLAIMED_UNDERGROUND_TOKEN = "select_claimed_underground_tokens"
    GET_OPPONENTS_PLAYED_CARDS = "get_opponents_played_cards"
    GET_MY_PLAYED_CARDS = "get_my_played_cards"
    GET_MARS_BOARD_STATE = "get_mars_board_state"


@dataclass
class SessionConfig:
    base_url: str = os.environ.get("TM_SERVER_URL", "http://localhost:8080")
    player_id: str | None = os.environ.get("TM_PLAYER_ID")


CFG = SessionConfig()
mcp = FastMCP("terraforming-mars", log_level="DEBUG", debug=True)

DEFAULT_LOG_LEVEL = os.environ.get("TM_MCP_LOG_LEVEL", "DEBUG").upper()
DEFAULT_LOG_FILE = os.environ.get(
    "TM_MCP_LOG_FILE",
    str(Path(__file__).parent / "tmp" / "terraforming-mars-mcp.log"),
)

_CARD_INFO_INDEX: dict[str, dict[str, Any]] | None = None
_LAST_OPPONENT_TABLEAU: dict[str, dict[str, Counter[str]]] = {}
TURN_WAIT_TIMEOUT_SECONDS = 2 * 60 * 60
TURN_WAIT_POLL_INTERVAL_SECONDS = 2
DETAIL_LEVEL_FULL = "full"
DETAIL_LEVEL_MINIMAL = "minimal"
VALID_DETAIL_LEVELS = {DETAIL_LEVEL_FULL, DETAIL_LEVEL_MINIMAL}


def _configure_server_logging(log_level: str, log_file: str) -> Path:
    normalized_level = log_level.upper()
    if normalized_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(f"Unsupported log level: {log_level}")

    log_path = Path(log_file).expanduser()
    if not log_path.is_absolute():
        log_path = (Path.cwd() / log_path).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, normalized_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
        force=True,
    )
    return log_path


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


def _get_player(player_id: str | None = None) -> dict[str, Any]:
    pid = _ensure_player_id(player_id)
    result = _http_json("GET", "/api/player", {"id": pid})
    if not isinstance(result, dict):
        raise RuntimeError("Unexpected /api/player response")
    return ApiPlayerViewModel.model_validate(result).model_dump(exclude_none=True)


def _post_input(response: dict[str, Any], player_id: str | None = None) -> dict[str, Any]:
    pid = _ensure_player_id(player_id)
    result = _http_json("POST", "/player/input", {"id": pid}, response)
    if not isinstance(result, dict):
        raise RuntimeError("Unexpected /player/input response")
    return ApiPlayerViewModel.model_validate(result).model_dump(exclude_none=True)


def _parse_card_list(value: list[str] | str | None, field_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, list):
        parsed: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError(f"{field_name} must contain only strings")
            trimmed = item.strip()
            if trimmed:
                parsed.append(trimmed)
        return parsed
    raise ValueError(f"{field_name} must be a list of strings or a comma-separated string")


class PaymentPayloadModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    mega_credits: int = Field(default=0, alias="megaCredits")
    steel: int = 0
    titanium: int = 0
    heat: int = 0
    plants: int = 0
    microbes: int = 0
    floaters: int = 0
    luna_archives_science: int = Field(default=0, alias="lunaArchivesScience")
    spire_science: int = Field(default=0, alias="spireScience")
    seeds: int = 0
    aurorai_data: int = Field(default=0, alias="auroraiData")
    graphene: int = 0
    kuiper_asteroids: int = Field(default=0, alias="kuiperAsteroids")


class InitialCardsSelectionModel(BaseModel):
    corporation_card: str | None = None
    project_cards: list[str]
    prelude_cards: list[str] = Field(default_factory=list)
    ceo_cards: list[str] = Field(default_factory=list)

    @field_validator("project_cards", "prelude_cards", "ceo_cards", mode="before")
    @classmethod
    def _normalize_cards(cls, value: list[str] | str | None, info: Any) -> list[str]:
        return _parse_card_list(value, str(info.field_name))


class OrChoiceInputModel(BaseModel):
    option_index: int = Field(ge=0)
    sub_response_json: str | dict[str, Any] | None = None

    @field_validator("sub_response_json", mode="before")
    @classmethod
    def _normalize_nested_response(cls, value: str | dict[str, Any] | None) -> dict[str, Any]:
        if value is None or value == "":
            return {"type": "option"}
        if isinstance(value, str):
            decoded = json.loads(value)
            if not isinstance(decoded, dict):
                raise ValueError("sub_response_json must decode to an object")
            return decoded
        if isinstance(value, dict):
            return value
        raise ValueError("sub_response_json must be a JSON string or object")


class RawInputEntityRequest(BaseModel):
    entity_json: str


def _get_waiting_for_model(player_model: dict[str, Any]) -> ApiWaitingForInputModel | None:
    raw_waiting_for = player_model.get("waitingFor")
    if isinstance(raw_waiting_for, ApiWaitingForInputModel):
        return raw_waiting_for
    if isinstance(raw_waiting_for, dict):
        return ApiWaitingForInputModel.model_validate(raw_waiting_for)
    return None


def _normalize_or_sub_response(value: str | dict[str, Any] | None) -> dict[str, Any]:
    if value is None or value == "":
        return {"type": "option"}
    if isinstance(value, str):
        decoded = json.loads(value)
        if not isinstance(decoded, dict):
            raise ValueError("sub_response_json must decode to an object")
        value = decoded
    if isinstance(value, dict):
        if "type" not in value:
            return {"type": "option", **value}
        return value
    raise ValueError("sub_response_json must be a JSON string or object")


def _find_or_option_index(waiting_for: ApiWaitingForInputModel, expected_type: str) -> int:
    options = waiting_for.options
    if not isinstance(options, list):
        raise RuntimeError("Current waitingFor has no options for an 'or' prompt")

    initial_idx = waiting_for.initialIdx
    if isinstance(initial_idx, int) and 0 <= initial_idx < len(options):
        initial_option = options[initial_idx]
        if isinstance(initial_option, ApiWaitingForInputModel) and initial_option.type == expected_type:
            return initial_idx

    for idx, option in enumerate(options):
        if isinstance(option, ApiWaitingForInputModel) and option.type == expected_type:
            return idx

    raise RuntimeError(f"No outer 'or' option of type '{expected_type}' is currently available")


def _normalize_raw_input_entity(entity: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(entity)
    entity_type = normalized.get("type")

    if entity_type in {"payment", "projectCard"}:
        payment = normalized.get("payment")
        if payment is None:
            normalized["payment"] = PaymentPayloadModel().model_dump(by_alias=True)
        elif isinstance(payment, dict):
            normalized["payment"] = PaymentPayloadModel.model_validate(payment).model_dump(by_alias=True)
    return normalized


def _get_waiting_for_state(game_age: int, undo_count: int, player_id: str | None = None) -> dict[str, Any]:
    pid = _ensure_player_id(player_id)
    result = _http_json(
        "GET",
        "/api/waitingfor",
        {"id": pid, "gameAge": str(game_age), "undoCount": str(undo_count)},
    )
    if not isinstance(result, dict):
        raise RuntimeError("Unexpected /api/waitingfor response")
    return ApiWaitingForStatusModel.model_validate(result).model_dump(exclude_none=True)


def _get_game_logs(player_id: str | None = None) -> list[dict[str, Any]]:
    pid = _ensure_player_id(player_id)
    result = _http_json("GET", "/api/game/logs", {"id": pid})
    if not isinstance(result, list):
        raise RuntimeError("Unexpected /api/game/logs response")
    normalized_logs: list[dict[str, Any]] = []
    for item in result:
        if not isinstance(item, dict):
            continue
        normalized_logs.append(ApiGameLogEntryModel.model_validate(item).model_dump(exclude_none=True))
    return normalized_logs


def _input_type_name(waiting_for: ApiWaitingForInputModel | None) -> str | None:
    if not waiting_for:
        return None
    value = waiting_for.type
    if isinstance(value, str):
        try:
            return InputType(value).value
        except ValueError:
            return value
    return None


def _best_effect_text(info: dict[str, Any]) -> str | None:
    on_play = info.get("on_play_effect_text")
    if isinstance(on_play, str) and on_play.strip():
        return on_play.strip()

    description = info.get("description_text")
    if isinstance(description, str) and description.strip():
        return description.strip()

    for key in ("ongoing_effects", "activated_actions"):
        values = info.get(key)
        if not isinstance(values, list):
            continue
        for value in values:
            if not isinstance(value, str):
                continue
            normalized = value.strip()
            if not normalized:
                continue
            if normalized.startswith("Effect:") or normalized.startswith("Action:"):
                _, _, normalized = normalized.partition(":")
                normalized = normalized.strip() or value.strip()
            return normalized
    return None


def _normalize_detail_level(detail_level: str) -> str:
    normalized = str(detail_level).strip().lower()
    if normalized not in VALID_DETAIL_LEVELS:
        raise ValueError(f"detail_level must be one of {sorted(VALID_DETAIL_LEVELS)}")
    return normalized


def _compact_card(
    card: dict[str, Any] | str | ApiCardModel,
    detail_level: str = DETAIL_LEVEL_FULL,
) -> dict[str, Any]:
    normalized_detail_level = _normalize_detail_level(detail_level)

    card_model: ApiCardModel | None = None
    if isinstance(card, str):
        card_name = card
    elif isinstance(card, ApiCardModel):
        card_model = card
        card_name = card_model.name
    else:
        card_model = ApiCardModel.model_validate(card)
        card_name = card_model.name

    info = _card_info(card_name, include_play_details=True)
    base_cost = info.get("base_cost")
    discounted_cost = card_model.calculatedCost if card_model and card_model.calculatedCost is not None else base_cost
    disabled = bool(card_model.isDisabled) if card_model else False
    warning = card_model.warning if card_model else None
    warnings = card_model.warnings if card_model else []
    resources = card_model.resources if card_model else None

    payload: dict[str, Any] = {
        "name": card_name,
    }
    cost = base_cost if base_cost is not None else discounted_cost
    if cost is not None:
        payload["cost"] = cost
    if discounted_cost is not None and discounted_cost != cost:
        payload["discounted_cost"] = discounted_cost
    if disabled:
        payload["disabled"] = True
    if isinstance(warning, str) and warning.strip():
        payload["warning"] = warning
    if isinstance(warnings, list) and warnings:
        payload["warnings"] = warnings
    if resources is not None:
        payload["resources"] = resources
    vp = info.get("vp")
    if vp is not None:
        payload["vp"] = vp

    if normalized_detail_level == DETAIL_LEVEL_FULL:
        tags = info.get("tags")
        if isinstance(tags, list) and tags:
            payload["tags"] = tags

        ongoing_effects = info.get("ongoing_effects")
        if isinstance(ongoing_effects, list) and ongoing_effects:
            payload["ongoing_effects"] = ongoing_effects

        activated_actions = info.get("activated_actions")
        if isinstance(activated_actions, list) and activated_actions:
            payload["activated_actions"] = activated_actions

        play_requirements = info.get("play_requirements")
        if isinstance(play_requirements, list) and play_requirements:
            payload["play_requirements"] = play_requirements

        play_requirements_text = info.get("play_requirements_text")
        if isinstance(play_requirements_text, str) and play_requirements_text.strip():
            payload["play_requirements_text"] = play_requirements_text

        on_play_effect_text = info.get("on_play_effect_text")
        if isinstance(on_play_effect_text, str) and on_play_effect_text.strip():
            payload["on_play_effect_text"] = on_play_effect_text

        effect_text = _best_effect_text(info)
        if isinstance(effect_text, str) and effect_text.strip():
            payload["effect_text"] = effect_text

    return payload


def _compact_cards(
    cards: list[Any],
    detail_level: str = DETAIL_LEVEL_FULL,
) -> list[dict[str, Any]]:
    compact_cards: list[dict[str, Any]] = []
    for card in cards:
        compact = _compact_card(card, detail_level=detail_level)
        if compact:
            compact_cards.append(compact)
    return compact_cards


def _load_card_info_index() -> dict[str, dict[str, Any]]:
    global _CARD_INFO_INDEX
    if _CARD_INFO_INDEX is not None:
        return _CARD_INFO_INDEX

    cards_file = Path(__file__).resolve().parents[1] / "submodules" / "tm-oss-server" / "src" / "genfiles" / "cards.json"
    if not cards_file.exists():
        _CARD_INFO_INDEX = {}
        return _CARD_INFO_INDEX

    raw = json.loads(cards_file.read_text(encoding="utf-8"))
    index: dict[str, dict[str, Any]] = {}
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                name = item.get("name")
                if isinstance(name, str):
                    index[name] = item
    _CARD_INFO_INDEX = index
    return _CARD_INFO_INDEX


def _extract_strings(node: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(node, str):
        strings.append(node)
    elif isinstance(node, list):
        for value in node:
            strings.extend(_extract_strings(value))
    elif isinstance(node, dict):
        for value in node.values():
            strings.extend(_extract_strings(value))
    return strings


def _description_text(metadata: dict[str, Any] | None) -> str | None:
    if not isinstance(metadata, dict):
        return None
    description = metadata.get("description")
    if isinstance(description, str):
        return description
    if isinstance(description, dict):
        text = description.get("text")
        if isinstance(text, str):
            return text
    return None


def _split_requirement_and_effect(description: str | None) -> tuple[str | None, str | None]:
    if not description:
        return None, None
    match = re.match(
        r"^(Requires .*?\.|It must be .*?\.|[A-Za-z ]+ must be .*?\.)\s*(.*)$",
        description,
    )
    if not match:
        return None, description
    requirement_text = match.group(1).strip()
    effect_text = match.group(2).strip() or None
    return requirement_text, effect_text


def _extract_actions_and_effects(render_data: Any) -> tuple[list[str], list[str]]:
    actions: list[str] = []
    effects: list[str] = []
    for text in _extract_strings(render_data):
        normalized = text.strip()
        if normalized.startswith("Action:"):
            actions.append(normalized)
        elif normalized.startswith("Effect:"):
            effects.append(normalized)
    return actions, effects


def _format_vp(vp: Any) -> int | str | None:
    """Return a human-readable VP value, or None if VP is zero/absent."""
    if vp is None:
        return None
    if isinstance(vp, (int, float)):
        return int(vp) if vp != 0 else None
    if not isinstance(vp, dict):
        return None
    per: int = vp.get("per", 1) or 1
    each: int = vp.get("each", 1) or 1
    if "resourcesHere" in vp:
        if each != 1:
            return f"{each} per resource"
        if per != 1:
            return f"1 per {per} resources"
        return "1 per resource"
    if "tag" in vp:
        tag = vp["tag"]
        if per != 1:
            return f"1 per {per} {tag} tags"
        return f"1 per {tag} tag"
    if "cities" in vp:
        suffix = " (all players)" if vp.get("all") else ""
        if per != 1:
            return f"1 per {per} cities{suffix}"
        return f"1 per city{suffix}"
    if "colonies" in vp:
        suffix = " (all players)" if vp.get("all") else ""
        if per != 1:
            return f"1 per {per} colonies{suffix}"
        return f"1 per colony{suffix}"
    if "moon" in vp:
        moon_obj = vp.get("moon")
        tile = next(iter(moon_obj), "tile") if isinstance(moon_obj, dict) and moon_obj else "tile"
        if per != 1:
            return f"1 per {per} {tile} tiles on Moon"
        return f"1 per {tile} tile on Moon"
    return None


def _card_info(card_name: Any, include_play_details: bool = False) -> dict[str, Any]:
    if not isinstance(card_name, str):
        return {}
    card = _load_card_info_index().get(card_name)
    if not isinstance(card, dict):
        return {}

    tags = card.get("tags") if isinstance(card.get("tags"), list) else []
    metadata = card.get("metadata") if isinstance(card.get("metadata"), dict) else None
    render_data = metadata.get("renderData") if isinstance(metadata, dict) else None
    description = _description_text(metadata)
    actions, effects = _extract_actions_and_effects(render_data)
    vp = _format_vp(card.get("victoryPoints"))

    info: dict[str, Any] = {
        "name": card_name,
        "tags": tags,
        "ongoing_effects": effects,
        "activated_actions": actions,
        "description_text": description,
        "vp": vp,
    }

    if include_play_details:
        req_text, on_play = _split_requirement_and_effect(description)
        requirements = card.get("requirements") if isinstance(card.get("requirements"), list) else []
        info.update(
            {
                "base_cost": card.get("cost"),
                "play_requirements": requirements,
                "play_requirements_text": req_text,
                "on_play_effect_text": on_play,
            }
        )
    return info


def _normalize_waiting_for(
    waiting_for: ApiWaitingForInputModel | None,
    depth: int = 0,
    detail_level: str = DETAIL_LEVEL_FULL,
) -> dict[str, Any] | None:
    if waiting_for is None:
        return None

    wf = waiting_for

    normalized: dict[str, Any] = {
        "input_type": _input_type_name(wf),
        "title": wf.title,
        "button_label": wf.buttonLabel,
    }

    if wf.warning is not None:
        normalized["warning"] = wf.warning
    if isinstance(wf.warnings, list) and wf.warnings:
        normalized["warnings"] = wf.warnings

    if wf.initialIdx is not None:
        normalized["initial_index"] = wf.initialIdx

    if wf.min is not None or wf.max is not None:
        amount_range: dict[str, Any] = {}
        if wf.min is not None:
            amount_range["min"] = wf.min
        if wf.max is not None:
            amount_range["max"] = wf.max
        if wf.maxByDefault is not None:
            amount_range["max_by_default"] = wf.maxByDefault
        normalized["amount_range"] = amount_range

    if wf.amount is not None:
        normalized["amount"] = wf.amount

    if wf.count is not None:
        normalized["count"] = wf.count

    if isinstance(wf.include, list) and wf.include:
        normalized["include"] = wf.include

    if isinstance(wf.cards, list):
        normalized["cards"] = _compact_cards(wf.cards, detail_level=detail_level)
        card_selection: dict[str, Any] = {}
        if wf.min is not None:
            card_selection["min"] = wf.min
        if wf.max is not None:
            card_selection["max"] = wf.max
        if wf.selectBlueCardAction is True:
            card_selection["select_blue_card_action"] = True
        if wf.showOnlyInLearnerMode is True:
            card_selection["show_only_in_learner_mode"] = True
        if wf.showOwner is True:
            card_selection["show_owner"] = True
        if card_selection:
            normalized["card_selection"] = card_selection

    if isinstance(wf.players, list) and wf.players:
        normalized["players"] = wf.players
    if isinstance(wf.spaces, list) and wf.spaces:
        normalized["spaces"] = wf.spaces
    if isinstance(wf.parties, list) and wf.parties:
        normalized["parties"] = wf.parties
    if isinstance(wf.globalEventNames, list) and wf.globalEventNames:
        normalized["globalEventNames"] = wf.globalEventNames

    if isinstance(wf.tokens, list) and wf.tokens:
        normalized["tokens"] = [token.model_dump(exclude_none=True) for token in wf.tokens]

    if isinstance(wf.coloniesModel, list):
        normalized["colonies"] = [colony.name for colony in wf.coloniesModel if isinstance(colony.name, str)]

    if isinstance(wf.payProduction, dict):
        normalized["pay_production"] = wf.payProduction

    if isinstance(wf.paymentOptions, dict):
        normalized["payment_options"] = wf.paymentOptions

    if isinstance(wf.aresData, dict):
        normalized["ares_data"] = wf.aresData.get("hazardData", wf.aresData)

    if isinstance(wf.options, list):
        if depth >= 2:
            normalized["options_count"] = len(wf.options)
        else:
            normalized_options: list[dict[str, Any]] = []
            for idx, option in enumerate(wf.options):
                option_detail = _normalize_waiting_for(option, depth + 1, detail_level=detail_level)
                option_payload: dict[str, Any] = {
                    "index": idx,
                    "title": option.title,
                    "input_type": _input_type_name(option),
                }
                if option_detail is not None:
                    option_payload["detail"] = option_detail
                if wf.initialIdx is not None:
                    option_payload["is_initial"] = idx == wf.initialIdx

                normalized_options.append(option_payload)

            normalized["options"] = normalized_options

    return normalized


def _summarize_players(player_model: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    parsed_view = ApiPlayerViewModel.model_validate(player_model)
    this_player = parsed_view.thisPlayer
    player_color = player_model.get("color")
    if not isinstance(player_color, str) and isinstance(this_player, ApiPublicPlayerModel):
        this_color = this_player.color
        if isinstance(this_color, str):
            player_color = this_color

    you: dict[str, Any] = {}
    others: list[dict[str, Any]] = []
    all_players = parsed_view.players or []
    for p in all_players:
        if not isinstance(p, ApiPublicPlayerModel):
            continue
        compact = {
            "name": p.name,
            "color": p.color,
            "active": p.isActive,
            "tr": p.terraformRating,
            "mc": p.megaCredits,
            "steel": p.steel,
            "titanium": p.titanium,
            "plants": p.plants,
            "energy": p.energy,
            "heat": p.heat,
            "prod": {
                "mc": p.megaCreditProduction,
                "steel": p.steelProduction,
                "titanium": p.titaniumProduction,
                "plants": p.plantProduction,
                "energy": p.energyProduction,
                "heat": p.heatProduction,
            },
            "cards_in_hand_count": p.cardsInHandNbr,
            "actions_this_generation": p.actionsThisGeneration,
        }
        if p.color == player_color:
            you = compact
        else:
            others.append(compact)

    if not you and isinstance(this_player, ApiPublicPlayerModel):
        you = {
            "name": this_player.name,
            "color": this_player.color,
            "active": this_player.isActive,
            "tr": this_player.terraformRating,
            "mc": this_player.megaCredits,
            "steel": this_player.steel,
            "titanium": this_player.titanium,
            "plants": this_player.plants,
            "energy": this_player.energy,
            "heat": this_player.heat,
            "prod": {
                "mc": this_player.megaCreditProduction,
                "steel": this_player.steelProduction,
                "titanium": this_player.titaniumProduction,
                "plants": this_player.plantProduction,
                "energy": this_player.energyProduction,
                "heat": this_player.heatProduction,
            },
            "cards_in_hand_count": this_player.cardsInHandNbr,
            "actions_this_generation": this_player.actionsThisGeneration,
        }
    return you, others


def _summarize_board(game: dict[str, Any]) -> dict[str, Any]:
    parsed_game = game if isinstance(game, dict) else {}
    spaces_raw = parsed_game.get("spaces")
    spaces = [ApiSpaceModel.model_validate(space) for space in spaces_raw] if isinstance(spaces_raw, list) else []
    occupied = 0
    by_tile: dict[str, int] = {}
    for space in spaces:
        tile_type = space.tileType
        if tile_type is not None:
            occupied += 1
            key = str(tile_type)
            by_tile[key] = by_tile.get(key, 0) + 1
    return {
        "total_spaces": len(spaces) if spaces else (len(spaces_raw) if isinstance(spaces_raw, list) else None),
        "occupied_spaces": occupied,
        "tile_counts": by_tile,
    }


def _summarize_milestones(game: dict[str, Any]) -> list[dict[str, Any]]:
    milestones_raw = game.get("milestones")
    if not isinstance(milestones_raw, list):
        return []

    summarized: list[dict[str, Any]] = []
    for raw_milestone in milestones_raw:
        milestone = ApiClaimedMilestoneModel.model_validate(raw_milestone)
        owner_color = milestone.color
        owner_name = milestone.playerName
        status = "claimed" if owner_color or owner_name else "available"

        scores: list[dict[str, Any]] = []
        claimable_by: list[str] = []
        for score in milestone.scores or []:
            compact = {
                "color": score.color,
                "score": score.score,
                "claimable": score.claimable is True,
            }
            scores.append(compact)
            if score.claimable is True and isinstance(score.color, str):
                claimable_by.append(score.color)

        summarized.append(
            {
                "name": milestone.name,
                "status": status,
                "owner_color": owner_color,
                "owner_name": owner_name,
                "scores": scores,
                "claimable_by": claimable_by,
            }
        )
    return summarized


def _summarize_awards(game: dict[str, Any]) -> list[dict[str, Any]]:
    awards_raw = game.get("awards")
    if not isinstance(awards_raw, list):
        return []

    summarized: list[dict[str, Any]] = []
    for raw_award in awards_raw:
        award = ApiFundedAwardModel.model_validate(raw_award)
        funder_color = award.color
        funder_name = award.playerName
        status = "funded" if funder_color or funder_name else "unfunded"

        scores: list[dict[str, Any]] = []
        for score in award.scores or []:
            scores.append(
                {
                    "color": score.color,
                    "score": score.score,
                }
            )

        summarized.append(
            {
                "name": award.name,
                "status": status,
                "funder_color": funder_color,
                "funder_name": funder_name,
                "scores": scores,
            }
        )
    return summarized


END_OF_GENERATION_PHASES = {"production", "solar", "intergeneration", "end"}


def _full_board_state(game: dict[str, Any], include_empty_spaces: bool = False) -> dict[str, Any]:
    spaces = game.get("spaces")
    mars_spaces: list[dict[str, Any]] = []
    if isinstance(spaces, list):
        for raw_space in spaces:
            if not isinstance(raw_space, dict):
                continue
            space = ApiSpaceModel.model_validate(raw_space)
            if not include_empty_spaces and space.tileType is None:
                continue
            mars_spaces.append(
                {
                    "id": space.id,
                    "x": space.x,
                    "y": space.y,
                    "space_type": space.spaceType,
                    "bonus": space.bonus,
                    "tile_type": space.tileType,
                    "owner_color": space.color,
                    "co_owner_color": space.coOwner,
                    "highlight": space.highlight,
                    "gagarin": space.gagarin,
                    "rotated": space.rotated,
                    "cathedral": space.cathedral,
                    "nomads": space.nomads,
                    "underground_resource": space.undergroundResource,
                    "excavator": space.excavator,
                }
            )

    return {
        "game_id": game.get("id"),
        "phase": game.get("phase"),
        "generation": game.get("generation"),
        "globals": {
            "temperature": game.get("temperature"),
            "oxygen": game.get("oxygenLevel"),
            "oceans": game.get("oceans"),
            "venus": game.get("venusScaleLevel"),
            "terraformed": game.get("isTerraformed"),
        },
        "summary": _summarize_board(game),
        "spaces": mars_spaces,
    }


def _extract_played_cards(player: dict[str, Any], include_play_details: bool = False) -> list[dict[str, Any]]:
    parsed_player = ApiPublicPlayerModel.model_validate(player)
    tableau = parsed_player.tableau
    cards: list[dict[str, Any]] = []
    if isinstance(tableau, list):
        for card in tableau:
            info = _card_info(card.name, include_play_details=include_play_details)
            payload: dict[str, Any] = {
                "name": card.name,
                "resources": card.resources,
                "is_disabled": card.isDisabled is True,
                "clone_tag": card.cloneTag,
                "tags": info.get("tags", []),
                "ongoing_effects": info.get("ongoing_effects", []),
                "activated_actions": info.get("activated_actions", []),
            }
            vp = info.get("vp")
            if vp is not None:
                payload["vp"] = vp
            if include_play_details:
                base_cost = info.get("base_cost")
                discounted_cost = card.calculatedCost if card.calculatedCost is not None else base_cost
                payload.update(
                    {
                        "play_requirements": info.get("play_requirements", []),
                        "play_requirements_text": info.get("play_requirements_text"),
                        "on_play_effect_text": info.get("on_play_effect_text"),
                        "cost": base_cost if base_cost is not None else discounted_cost,
                        "discounted_cost": discounted_cost,
                    }
                )
            cards.append(payload)
    return cards


def _detect_new_opponent_cards(player_model: dict[str, Any]) -> list[dict[str, Any]]:
    parsed_view = ApiPlayerViewModel.model_validate(player_model)
    if parsed_view.game is None:
        return []
    game_id = parsed_view.game.id
    pid = parsed_view.id or CFG.player_id
    if not isinstance(game_id, str) or not isinstance(pid, str):
        return []
    key = f"{game_id}:{pid}"

    this_color = parsed_view.thisPlayer.color if isinstance(parsed_view.thisPlayer, ApiPublicPlayerModel) else None
    players = parsed_view.players or []

    current: dict[str, Counter[str]] = {}
    for player in players:
        color = player.color
        if color == this_color:
            continue
        tableau = player.tableau or []
        names = [card.name for card in tableau if isinstance(card.name, str)]
        if isinstance(color, str):
            current[color] = Counter(names)

    previous = _LAST_OPPONENT_TABLEAU.get(key, {})
    events: list[dict[str, Any]] = []
    for player in players:
        color = player.color
        if not isinstance(color, str) or color == this_color:
            continue
        old_counts = previous.get(color, Counter())
        new_counts = current.get(color, Counter())
        delta = new_counts - old_counts
        for card_name, count in delta.items():
            for _ in range(count):
                info = _card_info(card_name, include_play_details=True)
                event: dict[str, Any] = {
                    "player_name": player.name,
                    "player_color": color,
                    "card_name": card_name,
                    "tags": info.get("tags", []),
                    "ongoing_effects": info.get("ongoing_effects", []),
                    "activated_actions": info.get("activated_actions", []),
                    "play_requirements": info.get("play_requirements", []),
                    "play_requirements_text": info.get("play_requirements_text"),
                    "on_play_effect_text": info.get("on_play_effect_text"),
                    "cost": info.get("base_cost"),
                    "discounted_cost": info.get("base_cost"),
                }
                vp = info.get("vp")
                if vp is not None:
                    event["vp"] = vp
                events.append(event)

    _LAST_OPPONENT_TABLEAU[key] = current
    return events


def _action_tools_for_input_type(input_type: str | None) -> list[str]:
    if input_type is None:
        return []
    try:
        input_type_enum = InputType(input_type)
    except ValueError:
        return [ToolName.SUBMIT_RAW_ENTITY.value]

    match input_type_enum:
        case InputType.AND_OPTIONS:
            tools = [ToolName.SUBMIT_AND_OPTIONS.value]
        case InputType.OR_OPTIONS:
            tools = [ToolName.CHOOSE_OR_OPTION.value]
        case InputType.SELECT_AMOUNT:
            tools = [ToolName.SELECT_AMOUNT.value]
        case InputType.SELECT_CARD:
            tools = [ToolName.SELECT_CARDS.value]
        case InputType.SELECT_DELEGATE:
            tools = [ToolName.SELECT_DELEGATE_TARGET.value]
        case InputType.SELECT_PAYMENT:
            tools = [ToolName.PAY_FOR_ACTION.value]
        case InputType.SELECT_PROJECT_CARD_TO_PLAY:
            tools = [ToolName.PAY_FOR_PROJECT_CARD.value]
        case InputType.SELECT_INITIAL_CARDS:
            tools = [ToolName.SELECT_INITIAL_CARDS.value]
        case InputType.SELECT_OPTION:
            tools = [ToolName.CONFIRM_OPTION.value]
        case InputType.SELECT_PARTY:
            tools = [ToolName.SELECT_PARTY.value]
        case InputType.SELECT_PLAYER:
            tools = [ToolName.SELECT_PLAYER.value]
        case InputType.SELECT_SPACE:
            tools = [ToolName.SELECT_SPACE.value]
        case InputType.SELECT_COLONY:
            tools = [ToolName.SELECT_COLONY.value]
        case InputType.SELECT_PRODUCTION_TO_LOSE:
            tools = [ToolName.SELECT_PRODUCTION_TO_LOSE.value]
        case InputType.SHIFT_ARES_GLOBAL_PARAMETERS:
            tools = [ToolName.SHIFT_ARES_GLOBAL_PARAMETERS.value]
        case InputType.SELECT_GLOBAL_EVENT:
            tools = [ToolName.SELECT_GLOBAL_EVENT.value]
        case InputType.SELECT_POLICY:
            tools = [ToolName.SELECT_POLICY.value]
        case InputType.SELECT_RESOURCE:
            tools = [ToolName.SELECT_RESOURCE.value]
        case InputType.SELECT_RESOURCES:
            tools = [ToolName.SELECT_RESOURCES.value]
        case InputType.SELECT_CLAIMED_UNDERGROUND_TOKEN:
            tools = [ToolName.SELECT_CLAIMED_UNDERGROUND_TOKEN.value]

    if ToolName.SUBMIT_RAW_ENTITY.value not in tools:
        tools.append(ToolName.SUBMIT_RAW_ENTITY.value)
    return tools


def _build_agent_state(
    player_model: dict[str, Any],
    include_full_model: bool = False,
    include_board_state: bool = False,
    detail_level: str = DETAIL_LEVEL_FULL,
) -> dict[str, Any]:
    normalized_detail_level = _normalize_detail_level(detail_level)
    game = player_model.get("game", {}) if isinstance(player_model.get("game"), dict) else {}
    waiting_for = _get_waiting_for_model(player_model)
    input_type = _input_type_name(waiting_for)
    you, opponents = _summarize_players(player_model)

    phase = game.get("phase")
    show_board = include_board_state or (
        normalized_detail_level == DETAIL_LEVEL_FULL
        and isinstance(phase, str)
        and phase in END_OF_GENERATION_PHASES
    )

    session: dict[str, Any] = {
        "player_id": player_model.get("id", CFG.player_id),
    }
    if normalized_detail_level == DETAIL_LEVEL_FULL:
        session["base_url"] = CFG.base_url

    game_state: dict[str, Any] = {
        "id": game.get("id"),
        "phase": game.get("phase"),
        "generation": game.get("generation"),
        "terraforming": {
            "temperature": game.get("temperature"),
            "oxygen": game.get("oxygenLevel"),
            "oceans": game.get("oceans"),
            "venus": game.get("venusScaleLevel"),
            "terraformed": game.get("isTerraformed"),
        },
        "game_age": game.get("gameAge"),
        "undo_count": game.get("undoCount"),
        "passed_players": game.get("passedPlayers"),
    }

    if normalized_detail_level == DETAIL_LEVEL_FULL:
        game_state.update(
            {
                "milestones": _summarize_milestones(game),
                "awards": _summarize_awards(game),
            }
        )
    if show_board:
        game_state["board"] = _summarize_board(game)
        game_state["board_visible"] = True
    elif normalized_detail_level == DETAIL_LEVEL_FULL:
        game_state["board"] = None
        game_state["board_visible"] = False

    if normalized_detail_level == DETAIL_LEVEL_FULL:
        opponents_state = opponents
        opponent_card_events = _detect_new_opponent_cards(player_model)
    else:
        opponents_state = [
            {
                "name": p.get("name"),
                "color": p.get("color"),
                "active": p.get("active"),
                "tr": p.get("tr"),
                "cards_in_hand_count": p.get("cards_in_hand_count"),
            }
            for p in opponents
        ]
        opponent_card_events = []

    result: dict[str, Any] = {
        "session": session,
        "game": game_state,
        "you": you,
        "opponents": opponents_state,
        "waiting_for": _normalize_waiting_for(waiting_for, detail_level=normalized_detail_level),
        "suggested_tools": _action_tools_for_input_type(input_type),
        "opponent_card_events": opponent_card_events,
    }

    if include_full_model:
        result["raw_player_model"] = player_model
    return result


def _has_waiting_input(player_model: dict[str, Any]) -> bool:
    return _get_waiting_for_model(player_model) is not None


def _log_signature(entry: dict[str, Any]) -> str:
    return json.dumps(
        {
            "timestamp": entry.get("timestamp"),
            "message": entry.get("message"),
            "data": entry.get("data"),
            "type": entry.get("type"),
            "playerId": entry.get("playerId"),
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _build_color_name_map(player_model: dict[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    players = player_model.get("players")
    if not isinstance(players, list):
        return mapping
    for p in players:
        if not isinstance(p, dict):
            continue
        color = p.get("color")
        name = p.get("name")
        if isinstance(color, str) and isinstance(name, str):
            mapping[color] = name
    return mapping


def _format_log_entry(entry: dict[str, Any], color_to_name: dict[str, str]) -> str:
    template = entry.get("message")
    data = entry.get("data")
    if not isinstance(template, str) or not isinstance(data, list):
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
        if data_type == "player" and isinstance(value, str):
            return color_to_name.get(value, value)
        if value is None:
            return ""
        return str(value)

    return re.sub(r"\$\{(\d{1,2})\}", replace, template)


def _extract_opponent_actions(
    initial_logs: list[dict[str, Any]],
    final_logs: list[dict[str, Any]],
    opponent_colors: set[str],
    color_to_name: dict[str, str],
) -> list[str]:
    seen = {_log_signature(entry) for entry in initial_logs}
    actions: list[str] = []
    for entry in final_logs:
        signature = _log_signature(entry)
        if signature in seen:
            continue
        data = entry.get("data")
        if not isinstance(data, list):
            continue
        has_opponent = False
        for datum in data:
            if not isinstance(datum, dict):
                continue
            if datum.get("type") == "player" and datum.get("value") in opponent_colors:
                has_opponent = True
                break
        if has_opponent:
            actions.append(_format_log_entry(entry, color_to_name))
    return actions


def _wait_for_turn_from_player_model(
    player_model: dict[str, Any],
    initial_logs: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    game = player_model.get("game", {})
    if not isinstance(game, dict):
        raise RuntimeError("Missing game object in player model")

    this_player = player_model.get("thisPlayer")
    this_color = this_player.get("color") if isinstance(this_player, dict) else None
    color_to_name = _build_color_name_map(player_model)
    opponent_colors = {color for color in color_to_name if color != this_color}
    start_logs = initial_logs if initial_logs is not None else _get_game_logs()

    game_age = int(game.get("gameAge", 0))
    undo_count = int(game.get("undoCount", 0))
    deadline = time.monotonic() + TURN_WAIT_TIMEOUT_SECONDS
    last_waitingfor: dict[str, Any] | None = None

    while True:
        waiting = _get_waiting_for_state(game_age, undo_count)
        if isinstance(waiting, dict):
            last_waitingfor = waiting
        status = waiting.get("result")
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
            refreshed_game = refreshed.get("game", {})
            if isinstance(refreshed_game, dict):
                game_age = int(refreshed_game.get("gameAge", game_age))
                undo_count = int(refreshed_game.get("undoCount", undo_count))
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


def _submit_and_return_state(response: dict[str, Any]) -> dict[str, Any]:
    player_model = _post_input(response)
    if not _has_waiting_input(player_model):
        initial_logs = _get_game_logs()
        refreshed, opponent_actions = _wait_for_turn_from_player_model(player_model, initial_logs=initial_logs)
        if opponent_actions:
            result = _build_agent_state(refreshed)
            result["opponent_actions_between_turns"] = opponent_actions
            return result
    return _build_agent_state(player_model)


@mcp.tool()
def configure_session(base_url: str | None = None, player_id: str | None = None) -> dict[str, Any]:
    """Set or update Terraforming Mars server URL and player ID for later tools."""
    if base_url:
        CFG.base_url = _strip_base_url(base_url)
    if player_id:
        CFG.player_id = player_id
    return {"base_url": CFG.base_url, "player_id": CFG.player_id}


@mcp.tool()
def get_game_state(
    include_full_model: bool = False,
    include_board_state: bool = False,
    detail_level: Literal["full", "minimal"] = "full",
) -> dict[str, Any]:
    """Fetch current player state plus compact, agent-friendly action/game summary."""
    player_model = _get_player()
    return _build_agent_state(
        player_model,
        include_full_model=include_full_model,
        include_board_state=include_board_state,
        detail_level=detail_level,
    )


@mcp.tool()
def get_opponents_played_cards() -> dict[str, Any]:
    """Return all cards currently in each opponent's tableau (played cards)."""
    player_model = _get_player()
    this_player = player_model.get("thisPlayer")
    this_color = this_player.get("color") if isinstance(this_player, dict) else None
    players = player_model.get("players")

    opponents: list[dict[str, Any]] = []
    if isinstance(players, list):
        for player in players:
            if not isinstance(player, dict):
                continue
            if player.get("color") == this_color:
                continue
            played_cards = _extract_played_cards(player, include_play_details=True)
            opponents.append(
                {
                    "name": player.get("name"),
                    "color": player.get("color"),
                    "played_cards_count": len(played_cards),
                    "played_cards": played_cards,
                }
            )

    game = player_model.get("game", {}) if isinstance(player_model.get("game"), dict) else {}
    return {"generation": game.get("generation"), "phase": game.get("phase"), "opponents": opponents}


@mcp.tool()
def get_my_played_cards() -> dict[str, Any]:
    """Return all cards currently in your tableau (played cards)."""
    player_model = _get_player()
    this_player = player_model.get("thisPlayer")
    if not isinstance(this_player, dict):
        raise RuntimeError("Missing thisPlayer in /api/player response")

    cards = _extract_played_cards(this_player)
    game = player_model.get("game", {}) if isinstance(player_model.get("game"), dict) else {}
    return {
        "generation": game.get("generation"),
        "phase": game.get("phase"),
        "player": this_player.get("name"),
        "color": this_player.get("color"),
        "played_cards_count": len(cards),
        "played_cards": cards,
    }


@mcp.tool()
def get_mars_board_state(include_empty_spaces: bool = False) -> dict[str, Any]:
    """Return detailed Mars board state. This is the explicit board-inspection tool."""
    player_model = _get_player()
    game = player_model.get("game", {})
    if not isinstance(game, dict):
        raise RuntimeError("Missing game object in /api/player response")
    return _full_board_state(game, include_empty_spaces=include_empty_spaces)


@mcp.tool()
def get_my_hand_cards() -> dict[str, Any]:
    """Return all cards currently in your hand."""
    player_model = _get_player()
    this_player = player_model.get("thisPlayer")
    if not isinstance(this_player, dict):
        raise RuntimeError("Missing thisPlayer in /api/player response")

    raw_cards = player_model.get("cardsInHand")
    cards = _compact_cards(raw_cards) if isinstance(raw_cards, list) else []
    game = player_model.get("game", {}) if isinstance(player_model.get("game"), dict) else {}
    return {
        "generation": game.get("generation"),
        "phase": game.get("phase"),
        "player": this_player.get("name"),
        "color": this_player.get("color"),
        "cards_in_hand_count": len(cards),
        "cards_in_hand": cards,
    }


@mcp.tool()
def wait_for_turn() -> dict[str, Any]:
    """Poll /api/waitingfor until it's your turn using fixed server defaults."""
    player_model = _get_player()
    if _has_waiting_input(player_model):
        return {"status": "GO", "state": _build_agent_state(player_model)}
    refreshed, opponent_actions = _wait_for_turn_from_player_model(player_model)
    result = {"status": "GO", "state": _build_agent_state(refreshed)}
    if opponent_actions:
        result["opponent_actions_between_turns"] = opponent_actions
    return result


@mcp.tool()
def submit_raw_entity(request: RawInputEntityRequest) -> dict[str, Any]:
    """Submit any raw /player/input payload as a JSON object with `type`."""
    entity = json.loads(request.entity_json)
    if not isinstance(entity, dict):
        raise ValueError("entity_json must decode to an object")
    if "type" not in entity:
        raise ValueError("entity_json must include a 'type' field")
    return _submit_and_return_state(_normalize_raw_input_entity(entity))


@mcp.tool()
def choose_or_option(
    option_index: int | None = None,
    sub_response_json: str | dict[str, Any] | None = None,
    request: str | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Respond to `type: or` with selected index and nested response object.

    Accepts either direct params (`option_index`, `sub_response_json`) or a
    legacy JSON `request` payload.
    """
    if request is not None:
        parsed_request: dict[str, Any]
        if isinstance(request, str):
            decoded = json.loads(request)
            if not isinstance(decoded, dict):
                raise ValueError("request must decode to an object")
            parsed_request = decoded
        elif isinstance(request, dict):
            parsed_request = request
        else:
            raise ValueError("request must be a JSON string or object")

        if option_index is None:
            index_value = parsed_request.get("option_index", parsed_request.get("index"))
            if isinstance(index_value, int):
                option_index = index_value
            elif isinstance(index_value, str) and index_value.isdigit():
                option_index = int(index_value)
            elif index_value is not None:
                raise ValueError("request.option_index/index must be an integer")

        if sub_response_json is None:
            if "sub_response_json" in parsed_request:
                sub_response_json = parsed_request["sub_response_json"]
            elif "response" in parsed_request:
                sub_response_json = parsed_request["response"]

    if option_index is None:
        raise ValueError("option_index is required")

    return _submit_and_return_state(
        {
            "type": "or",
            "index": int(option_index),
            "response": _normalize_or_sub_response(sub_response_json),
        }
    )


@mcp.tool()
def submit_and_options(responses_json: str) -> dict[str, Any]:
    """Respond to `type: and` with JSON list of InputResponse objects."""
    responses = json.loads(responses_json)
    if not isinstance(responses, list):
        raise ValueError("responses_json must decode to a list of objects")
    for item in responses:
        if not isinstance(item, dict):
            raise ValueError("Each response must be an object")
    return _submit_and_return_state({"type": "and", "responses": responses})


@mcp.tool()
def confirm_option() -> dict[str, Any]:
    """Respond to `type: option`."""
    player_model = _get_player()
    waiting_for = _get_waiting_for_model(player_model)
    if waiting_for is not None and waiting_for.type == InputType.OR_OPTIONS.value:
        index = 0
        initial_idx = waiting_for.initialIdx
        if isinstance(initial_idx, int) and initial_idx >= 0:
            index = initial_idx
        else:
            options = waiting_for.options
            if isinstance(options, list):
                for idx, option in enumerate(options):
                    if isinstance(option, ApiWaitingForInputModel) and option.type == InputType.SELECT_OPTION.value:
                        index = idx
                        break
        return _submit_and_return_state({"type": "or", "index": index, "response": {"type": "option"}})
    return _submit_and_return_state({"type": "option"})


@mcp.tool()
def select_amount(amount: int) -> dict[str, Any]:
    """Respond to `type: amount`."""
    return _submit_and_return_state({"type": "amount", "amount": int(amount)})


@mcp.tool()
def select_cards(card_names: list[str]) -> dict[str, Any]:
    """Respond to `type: card` with chosen card names."""
    return _submit_and_return_state({"type": "card", "cards": card_names})


@mcp.tool()
def select_player(player_color: str) -> dict[str, Any]:
    """Respond to `type: player`."""
    if not player_color:
        raise ValueError("player_color is required")
    return _submit_and_return_state({"type": "player", "player": player_color})


@mcp.tool()
def select_delegate_target(player_color_or_neutral: str) -> dict[str, Any]:
    """Respond to `type: delegate` with a player color or `NEUTRAL`."""
    if not player_color_or_neutral:
        raise ValueError("player_color_or_neutral is required")
    return _submit_and_return_state({"type": "delegate", "player": player_color_or_neutral})


@mcp.tool()
def select_space(space_id: str) -> dict[str, Any]:
    """Respond to `type: space` using a board space ID from `waiting_for.spaces`."""
    if not space_id:
        raise ValueError("space_id is required")
    return _submit_and_return_state({"type": "space", "spaceId": space_id})


@mcp.tool()
def select_party(party_name: str) -> dict[str, Any]:
    """Respond to `type: party`."""
    if not party_name:
        raise ValueError("party_name is required")
    return _submit_and_return_state({"type": "party", "partyName": party_name})


@mcp.tool()
def select_colony(colony_name: str) -> dict[str, Any]:
    """Respond to `type: colony`."""
    if not colony_name:
        raise ValueError("colony_name is required")
    return _submit_and_return_state({"type": "colony", "colonyName": colony_name})


def _encode_payment(
    mega_credits: int = 0,
    steel: int = 0,
    titanium: int = 0,
    heat: int = 0,
    plants: int = 0,
    microbes: int = 0,
    floaters: int = 0,
    luna_archives_science: int = 0,
    spire_science: int = 0,
    seeds: int = 0,
    aurorai_data: int = 0,
    graphene: int = 0,
    kuiper_asteroids: int = 0,
) -> dict[str, int]:
    return {
        "megaCredits": mega_credits,
        "steel": steel,
        "titanium": titanium,
        "heat": heat,
        "plants": plants,
        "microbes": microbes,
        "floaters": floaters,
        "lunaArchivesScience": luna_archives_science,
        "spireScience": spire_science,
        "seeds": seeds,
        "auroraiData": aurorai_data,
        "graphene": graphene,
        "kuiperAsteroids": kuiper_asteroids,
    }


@mcp.tool()
def pay_for_action(
    mega_credits: int = 0,
    steel: int = 0,
    titanium: int = 0,
    heat: int = 0,
    plants: int = 0,
    microbes: int = 0,
    floaters: int = 0,
    luna_archives_science: int = 0,
    spire_science: int = 0,
    seeds: int = 0,
    aurorai_data: int = 0,
    graphene: int = 0,
    kuiper_asteroids: int = 0,
) -> dict[str, Any]:
    """Respond to `type: payment`."""
    return _submit_and_return_state(
        {
            "type": "payment",
            "payment": _encode_payment(
                mega_credits=mega_credits,
                steel=steel,
                titanium=titanium,
                heat=heat,
                plants=plants,
                microbes=microbes,
                floaters=floaters,
                luna_archives_science=luna_archives_science,
                spire_science=spire_science,
                seeds=seeds,
                aurorai_data=aurorai_data,
                graphene=graphene,
                kuiper_asteroids=kuiper_asteroids,
            ),
        }
    )


@mcp.tool()
def pay_for_project_card(
    card_name: str,
    mega_credits: int = 0,
    steel: int = 0,
    titanium: int = 0,
    heat: int = 0,
    plants: int = 0,
    microbes: int = 0,
    floaters: int = 0,
    luna_archives_science: int = 0,
    spire_science: int = 0,
    seeds: int = 0,
    aurorai_data: int = 0,
    graphene: int = 0,
    kuiper_asteroids: int = 0,
) -> dict[str, Any]:
    """Respond to `type: projectCard`."""
    if not card_name:
        raise ValueError("card_name is required")
    project_card_response = {
        "type": "projectCard",
        "card": card_name,
        "payment": _encode_payment(
            mega_credits=mega_credits,
            steel=steel,
            titanium=titanium,
            heat=heat,
            plants=plants,
            microbes=microbes,
            floaters=floaters,
            luna_archives_science=luna_archives_science,
            spire_science=spire_science,
            seeds=seeds,
            aurorai_data=aurorai_data,
            graphene=graphene,
            kuiper_asteroids=kuiper_asteroids,
        ),
    }

    player_model = _get_player()
    waiting_for = _get_waiting_for_model(player_model)
    if waiting_for is not None and waiting_for.type == InputType.OR_OPTIONS.value:
        option_index = _find_or_option_index(waiting_for, InputType.SELECT_PROJECT_CARD_TO_PLAY.value)
        return _submit_and_return_state(
            {
                "type": "or",
                "index": option_index,
                "response": project_card_response,
            }
        )

    return _submit_and_return_state(project_card_response)


@mcp.tool()
def select_initial_cards(request: InitialCardsSelectionModel) -> dict[str, Any]:
    """Respond to `type: initialCards` using current waiting-for option order."""
    player_model = _get_player()
    waiting_for = _get_waiting_for_model(player_model)
    options = waiting_for.options if waiting_for is not None else None
    if not isinstance(options, list):
        raise RuntimeError("Current waitingFor has no options for initialCards")

    responses: list[dict[str, Any]] = []
    for option in options:
        if not isinstance(option, ApiWaitingForInputModel):
            raise RuntimeError("Invalid option in initialCards")
        title = str(option.title or "").lower()
        if "corporation" in title:
            cards = [request.corporation_card] if request.corporation_card else []
        elif "prelude" in title:
            cards = request.prelude_cards
        elif "ceo" in title:
            cards = request.ceo_cards
        else:
            cards = request.project_cards
        responses.append({"type": "card", "cards": cards})

    return _submit_and_return_state({"type": "initialCards", "responses": responses})


@mcp.tool()
def select_production_to_lose(
    megacredits: int = 0,
    steel: int = 0,
    titanium: int = 0,
    plants: int = 0,
    energy: int = 0,
    heat: int = 0,
) -> dict[str, Any]:
    """Respond to `type: productionToLose`."""
    return _submit_and_return_state(
        {
            "type": "productionToLose",
            "units": {
                "megacredits": megacredits,
                "steel": steel,
                "titanium": titanium,
                "plants": plants,
                "energy": energy,
                "heat": heat,
            },
        }
    )


@mcp.tool()
def shift_ares_global_parameters(
    low_ocean_delta: int = 0,
    high_ocean_delta: int = 0,
    temperature_delta: int = 0,
    oxygen_delta: int = 0,
) -> dict[str, Any]:
    """Respond to `type: aresGlobalParameters`. Values are expected in {-1,0,1}."""
    return _submit_and_return_state(
        {
            "type": "aresGlobalParameters",
            "response": {
                "lowOceanDelta": low_ocean_delta,
                "highOceanDelta": high_ocean_delta,
                "temperatureDelta": temperature_delta,
                "oxygenDelta": oxygen_delta,
            },
        }
    )


@mcp.tool()
def select_global_event(global_event_name: str) -> dict[str, Any]:
    """Respond to `type: globalEvent`."""
    if not global_event_name:
        raise ValueError("global_event_name is required")
    return _submit_and_return_state({"type": "globalEvent", "globalEventName": global_event_name})


@mcp.tool()
def select_policy(policy_id: str) -> dict[str, Any]:
    """Respond to `type: policy`."""
    if not policy_id:
        raise ValueError("policy_id is required")
    return _submit_and_return_state({"type": "policy", "policyId": policy_id})


@mcp.tool()
def select_resource(resource: str) -> dict[str, Any]:
    """Respond to `type: resource`."""
    if not resource:
        raise ValueError("resource is required")
    return _submit_and_return_state({"type": "resource", "resource": resource})


@mcp.tool()
def select_resources(
    megacredits: int = 0,
    steel: int = 0,
    titanium: int = 0,
    plants: int = 0,
    energy: int = 0,
    heat: int = 0,
) -> dict[str, Any]:
    """Respond to `type: resources`."""
    return _submit_and_return_state(
        {
            "type": "resources",
            "units": {
                "megacredits": megacredits,
                "steel": steel,
                "titanium": titanium,
                "plants": plants,
                "energy": energy,
                "heat": heat,
            },
        }
    )


@mcp.tool()
def select_claimed_underground_tokens(selected: list[int]) -> dict[str, Any]:
    """Respond to `type: claimedUndergroundToken`."""
    return _submit_and_return_state({"type": "claimedUndergroundToken", "selected": selected})


def main() -> None:
    parser = argparse.ArgumentParser(description="Terraforming Mars MCP server")
    parser.add_argument(
        "--base-url",
        default=None,
        help="Terraforming Mars server base URL (overrides TM_SERVER_URL)",
    )
    parser.add_argument(
        "--player-id",
        default=None,
        help="Player ID to use at startup (overrides TM_PLAYER_ID)",
    )
    parser.add_argument(
        "--log-level",
        default=DEFAULT_LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log level for server logging (overrides TM_MCP_LOG_LEVEL)",
    )
    parser.add_argument(
        "--log-file",
        default=DEFAULT_LOG_FILE,
        help="Path to log file (overrides TM_MCP_LOG_FILE)",
    )
    args = parser.parse_args()

    _configure_server_logging(args.log_level, args.log_file)

    if args.base_url:
        CFG.base_url = _strip_base_url(args.base_url)
    if args.player_id:
        CFG.player_id = args.player_id

    mcp.run()


if __name__ == "__main__":
    main()
