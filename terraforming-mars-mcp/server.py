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
import os
import re
import time
from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib import error, parse, request

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator


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
mcp = FastMCP("terraforming-mars")

_CARD_INFO_INDEX: dict[str, dict[str, Any]] | None = None
_LAST_OPPONENT_TABLEAU: dict[str, dict[str, Counter[str]]] = {}
TURN_WAIT_TIMEOUT_SECONDS = 2 * 60 * 60
TURN_WAIT_POLL_INTERVAL_SECONDS = 2


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
    return result


def _post_input(response: dict[str, Any], player_id: str | None = None) -> dict[str, Any]:
    pid = _ensure_player_id(player_id)
    result = _http_json("POST", "/player/input", {"id": pid}, response)
    if not isinstance(result, dict):
        raise RuntimeError("Unexpected /player/input response")
    return result


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
    return result


def _get_game_logs(player_id: str | None = None) -> list[dict[str, Any]]:
    pid = _ensure_player_id(player_id)
    result = _http_json("GET", "/api/game/logs", {"id": pid})
    if not isinstance(result, list):
        raise RuntimeError("Unexpected /api/game/logs response")
    return [item for item in result if isinstance(item, dict)]


def _input_type_name(waiting_for: dict[str, Any] | None) -> str | None:
    if not waiting_for:
        return None
    value = waiting_for.get("type")
    if isinstance(value, str):
        try:
            return InputType(value).value
        except ValueError:
            return value
    return None


def _compact_card(card: dict[str, Any]) -> dict[str, Any]:
    info = _card_info(card.get("name"), include_play_details=True)
    return {
        "name": card.get("name"),
        "cost": card.get("calculatedCost", card.get("cost")),
        "type": card.get("cardType"),
        "disabled": card.get("isDisabled", False),
        "warning": card.get("warning"),
        "resources": card.get("resources"),
        "tags": info.get("tags", []),
        "ongoing_effects": info.get("ongoing_effects", []),
        "activated_actions": info.get("activated_actions", []),
        "play_requirements": info.get("play_requirements", []),
        "play_requirements_text": info.get("play_requirements_text"),
        "on_play_effect_text": info.get("on_play_effect_text"),
    }


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


def _card_info(card_name: Any, include_play_details: bool = False) -> dict[str, Any]:
    if not isinstance(card_name, str):
        return {}
    card = _load_card_info_index().get(card_name)
    if not isinstance(card, dict):
        return {}

    tags = card.get("tags") if isinstance(card.get("tags"), list) else []
    metadata = card.get("metadata") if isinstance(card.get("metadata"), dict) else None
    render_data = metadata.get("renderData") if isinstance(metadata, dict) else None
    actions, effects = _extract_actions_and_effects(render_data)

    info: dict[str, Any] = {
        "tags": tags,
        "ongoing_effects": effects,
        "activated_actions": actions,
    }

    if include_play_details:
        description = _description_text(metadata)
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


def _normalize_waiting_for(waiting_for: dict[str, Any] | None, depth: int = 0) -> dict[str, Any] | None:
    if waiting_for is None:
        return None

    normalized: dict[str, Any] = {
        "input_type": _input_type_name(waiting_for),
        "title": waiting_for.get("title"),
        "button_label": waiting_for.get("buttonLabel"),
    }

    if "min" in waiting_for or "max" in waiting_for:
        normalized["amount_range"] = {
            "min": waiting_for.get("min"),
            "max": waiting_for.get("max"),
            "max_by_default": waiting_for.get("maxByDefault"),
        }

    if "amount" in waiting_for:
        normalized["amount"] = waiting_for.get("amount")

    cards = waiting_for.get("cards")
    if isinstance(cards, list):
        normalized["cards"] = [_compact_card(card) for card in cards if isinstance(card, dict)]
        normalized["card_selection"] = {
            "min": waiting_for.get("min"),
            "max": waiting_for.get("max"),
            "select_blue_card_action": waiting_for.get("selectBlueCardAction", False),
        }

    for key in ("players", "spaces", "parties", "globalEventNames"):
        value = waiting_for.get(key)
        if isinstance(value, list):
            normalized[key] = value

    colonies_model = waiting_for.get("coloniesModel")
    if isinstance(colonies_model, list):
        normalized["colonies"] = [c.get("name") for c in colonies_model if isinstance(c, dict)]

    pay_production = waiting_for.get("payProduction")
    if isinstance(pay_production, dict):
        normalized["pay_production"] = pay_production

    payment_options = waiting_for.get("paymentOptions")
    if isinstance(payment_options, dict):
        normalized["payment_options"] = payment_options

    ares_data = waiting_for.get("aresData")
    if isinstance(ares_data, dict):
        normalized["ares_data"] = ares_data.get("hazardData", ares_data)

    options = waiting_for.get("options")
    if isinstance(options, list):
        if depth >= 2:
            normalized["options_count"] = len(options)
        else:
            normalized["options"] = [
                {
                    "index": idx,
                    "title": option.get("title") if isinstance(option, dict) else None,
                    "input_type": _input_type_name(option) if isinstance(option, dict) else None,
                    "detail": _normalize_waiting_for(option, depth + 1) if isinstance(option, dict) else None,
                }
                for idx, option in enumerate(options)
            ]

    return normalized


def _summarize_players(player_model: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    this_player = player_model.get("thisPlayer")
    player_color = player_model.get("color")
    if not isinstance(player_color, str) and isinstance(this_player, dict):
        this_color = this_player.get("color")
        if isinstance(this_color, str):
            player_color = this_color

    you: dict[str, Any] = {}
    others: list[dict[str, Any]] = []
    all_players = player_model.get("players", [])
    if isinstance(all_players, list):
        for p in all_players:
            if not isinstance(p, dict):
                continue
            compact = {
                "name": p.get("name"),
                "color": p.get("color"),
                "active": p.get("isActive"),
                "tr": p.get("terraformRating"),
                "mc": p.get("megaCredits"),
                "steel": p.get("steel"),
                "titanium": p.get("titanium"),
                "plants": p.get("plants"),
                "energy": p.get("energy"),
                "heat": p.get("heat"),
                "prod": {
                    "mc": p.get("megaCreditProduction"),
                    "steel": p.get("steelProduction"),
                    "titanium": p.get("titaniumProduction"),
                    "plants": p.get("plantProduction"),
                    "energy": p.get("energyProduction"),
                    "heat": p.get("heatProduction"),
                },
                "cards_in_hand_count": p.get("cardsInHandNbr"),
                "actions_this_generation": p.get("actionsThisGeneration"),
            }
            if p.get("color") == player_color:
                you = compact
            else:
                others.append(compact)

    if not you and isinstance(this_player, dict):
        you = {
            "name": this_player.get("name"),
            "color": this_player.get("color"),
            "active": this_player.get("isActive"),
            "tr": this_player.get("terraformRating"),
            "mc": this_player.get("megaCredits"),
            "steel": this_player.get("steel"),
            "titanium": this_player.get("titanium"),
            "plants": this_player.get("plants"),
            "energy": this_player.get("energy"),
            "heat": this_player.get("heat"),
            "prod": {
                "mc": this_player.get("megaCreditProduction"),
                "steel": this_player.get("steelProduction"),
                "titanium": this_player.get("titaniumProduction"),
                "plants": this_player.get("plantProduction"),
                "energy": this_player.get("energyProduction"),
                "heat": this_player.get("heatProduction"),
            },
            "cards_in_hand_count": this_player.get("cardsInHandNbr"),
            "actions_this_generation": this_player.get("actionsThisGeneration"),
        }
    return you, others


def _summarize_board(game: dict[str, Any]) -> dict[str, Any]:
    spaces = game.get("spaces")
    occupied = 0
    by_tile: dict[str, int] = {}
    if isinstance(spaces, list):
        for space in spaces:
            if not isinstance(space, dict):
                continue
            tile_type = space.get("tileType")
            if tile_type is not None:
                occupied += 1
                key = str(tile_type)
                by_tile[key] = by_tile.get(key, 0) + 1
    return {
        "total_spaces": len(spaces) if isinstance(spaces, list) else None,
        "occupied_spaces": occupied,
        "tile_counts": by_tile,
    }


END_OF_GENERATION_PHASES = {"production", "solar", "intergeneration", "end"}


def _full_board_state(game: dict[str, Any], include_empty_spaces: bool = False) -> dict[str, Any]:
    spaces = game.get("spaces")
    mars_spaces: list[dict[str, Any]] = []
    if isinstance(spaces, list):
        for space in spaces:
            if not isinstance(space, dict):
                continue
            if not include_empty_spaces and space.get("tileType") is None:
                continue
            mars_spaces.append(
                {
                    "id": space.get("id"),
                    "x": space.get("x"),
                    "y": space.get("y"),
                    "space_type": space.get("spaceType"),
                    "bonus": space.get("bonus"),
                    "tile_type": space.get("tileType"),
                    "owner_color": space.get("color"),
                    "co_owner_color": space.get("coOwner"),
                    "highlight": space.get("highlight"),
                    "gagarin": space.get("gagarin"),
                    "rotated": space.get("rotated"),
                    "cathedral": space.get("cathedral"),
                    "nomads": space.get("nomads"),
                    "underground_resource": space.get("undergroundResource"),
                    "excavator": space.get("excavator"),
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
    tableau = player.get("tableau")
    cards: list[dict[str, Any]] = []
    if isinstance(tableau, list):
        for card in tableau:
            if not isinstance(card, dict):
                continue
            info = _card_info(card.get("name"), include_play_details=include_play_details)
            payload = {
                "name": card.get("name"),
                "resources": card.get("resources"),
                "is_disabled": card.get("isDisabled", False),
                "clone_tag": card.get("cloneTag"),
                "tags": info.get("tags", []),
                "ongoing_effects": info.get("ongoing_effects", []),
                "activated_actions": info.get("activated_actions", []),
            }
            if include_play_details:
                payload.update(
                    {
                        "play_requirements": info.get("play_requirements", []),
                        "play_requirements_text": info.get("play_requirements_text"),
                        "on_play_effect_text": info.get("on_play_effect_text"),
                        "cost": card.get("calculatedCost", info.get("base_cost")),
                    }
                )
            cards.append(payload)
    return cards


def _detect_new_opponent_cards(player_model: dict[str, Any]) -> list[dict[str, Any]]:
    game = player_model.get("game")
    if not isinstance(game, dict):
        return []
    game_id = game.get("id")
    pid = player_model.get("id", CFG.player_id)
    if not isinstance(game_id, str) or not isinstance(pid, str):
        return []
    key = f"{game_id}:{pid}"

    this_player = player_model.get("thisPlayer")
    this_color = this_player.get("color") if isinstance(this_player, dict) else None
    players = player_model.get("players")
    if not isinstance(players, list):
        return []

    current: dict[str, Counter[str]] = {}
    for player in players:
        if not isinstance(player, dict):
            continue
        color = player.get("color")
        if color == this_color:
            continue
        tableau = player.get("tableau")
        names: list[str] = []
        if isinstance(tableau, list):
            for card in tableau:
                if isinstance(card, dict):
                    name = card.get("name")
                    if isinstance(name, str):
                        names.append(name)
        if isinstance(color, str):
            current[color] = Counter(names)

    previous = _LAST_OPPONENT_TABLEAU.get(key, {})
    events: list[dict[str, Any]] = []
    for player in players:
        if not isinstance(player, dict):
            continue
        color = player.get("color")
        if not isinstance(color, str) or color == this_color:
            continue
        old_counts = previous.get(color, Counter())
        new_counts = current.get(color, Counter())
        delta = new_counts - old_counts
        for card_name, count in delta.items():
            for _ in range(count):
                info = _card_info(card_name, include_play_details=True)
                events.append(
                    {
                        "player_name": player.get("name"),
                        "player_color": color,
                        "card_name": card_name,
                        "tags": info.get("tags", []),
                        "ongoing_effects": info.get("ongoing_effects", []),
                        "activated_actions": info.get("activated_actions", []),
                        "play_requirements": info.get("play_requirements", []),
                        "play_requirements_text": info.get("play_requirements_text"),
                        "on_play_effect_text": info.get("on_play_effect_text"),
                        "cost": info.get("base_cost"),
                    }
                )

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
) -> dict[str, Any]:
    game = player_model.get("game", {}) if isinstance(player_model.get("game"), dict) else {}
    waiting_for = player_model.get("waitingFor") if isinstance(player_model.get("waitingFor"), dict) else None
    input_type = _input_type_name(waiting_for)
    you, opponents = _summarize_players(player_model)

    phase = game.get("phase")
    show_board = include_board_state or (isinstance(phase, str) and phase in END_OF_GENERATION_PHASES)

    result: dict[str, Any] = {
        "session": {
            "base_url": CFG.base_url,
            "player_id": player_model.get("id", CFG.player_id),
        },
        "game": {
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
            "board": _summarize_board(game) if show_board else None,
            "board_visible": show_board,
        },
        "you": you,
        "opponents": opponents,
        "waiting_for": _normalize_waiting_for(waiting_for),
        "suggested_tools": _action_tools_for_input_type(input_type),
        "opponent_card_events": _detect_new_opponent_cards(player_model),
    }

    if include_full_model:
        result["raw_player_model"] = player_model
    return result


def _has_waiting_input(player_model: dict[str, Any]) -> bool:
    return isinstance(player_model.get("waitingFor"), dict)


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
def get_game_state(include_full_model: bool = False, include_board_state: bool = False) -> dict[str, Any]:
    """Fetch current player state plus compact, agent-friendly action/game summary."""
    player_model = _get_player()
    return _build_agent_state(
        player_model,
        include_full_model=include_full_model,
        include_board_state=include_board_state,
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
def choose_or_option(request: OrChoiceInputModel) -> dict[str, Any]:
    """Respond to `type: or` with selected index and nested response object."""
    return _submit_and_return_state(
        {"type": "or", "index": request.option_index, "response": request.sub_response_json}
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
    return _submit_and_return_state(
        {
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
    )


@mcp.tool()
def select_initial_cards(request: InitialCardsSelectionModel) -> dict[str, Any]:
    """Respond to `type: initialCards` using current waiting-for option order."""
    player_model = _get_player()
    waiting_for = player_model.get("waitingFor")
    options = waiting_for.get("options") if isinstance(waiting_for, dict) else None
    if not isinstance(options, list):
        raise RuntimeError("Current waitingFor has no options for initialCards")

    responses: list[dict[str, Any]] = []
    for option in options:
        if not isinstance(option, dict):
            raise RuntimeError("Invalid option in initialCards")
        title = str(option.get("title", "")).lower()
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


if __name__ == "__main__":
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
    args = parser.parse_args()

    if args.base_url:
        CFG.base_url = _strip_base_url(args.base_url)
    if args.player_id:
        CFG.player_id = args.player_id

    mcp.run()
