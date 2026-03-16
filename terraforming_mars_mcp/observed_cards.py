from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .api_response_models import CardModel, PlayerViewModel

_REPO_OUTPUT_ROOT = Path("agent-prompts/agent_game_notes")
_IN_MEMORY_STATE: dict[str, dict[str, Any]] = {}

_DRAFT_TITLE_PATTERNS = (
    re.compile(r"select (?:a|two) card", re.IGNORECASE),
    re.compile(r"select card\(s\) to buy", re.IGNORECASE),
)


def _card_name(card: CardModel | str | object) -> str | None:
    if isinstance(card, str):
        return card.strip() or None
    if isinstance(card, CardModel):
        return card.name.strip() or None
    name = getattr(card, "name", None)
    if isinstance(name, str):
        stripped = name.strip()
        return stripped or None
    return None


def _message_text(title: object) -> str:
    if isinstance(title, str):
        return title
    message = getattr(title, "message", None)
    if isinstance(message, str):
        return message
    return ""


def _is_draft_prompt(player_model: PlayerViewModel) -> bool:
    waiting_for = player_model.waitingFor
    if waiting_for is None:
        return False
    title = _message_text(waiting_for.title)
    return any(pattern.search(title) for pattern in _DRAFT_TITLE_PATTERNS)


def _tracker_key(player_model: PlayerViewModel) -> str | None:
    game_id = player_model.game.id
    player_id = player_model.id
    if not game_id or not player_id:
        return None
    return f"{game_id}:{player_id}"


def _final_path_for(player_model: PlayerViewModel) -> Path | None:
    game_id = player_model.game.id
    if not game_id:
        return None
    date_slug = datetime.now().strftime("%Y_%m_%d")
    return _REPO_OUTPUT_ROOT / date_slug / f"observed-cards-{game_id}.json"


def _empty_state() -> dict[str, Any]:
    return {
        "game_id": "",
        "player_id": "",
        "self_player": "",
        "generation": 0,
        "draft": {
            "seen_card_names": [],
            "drafted_card_names": [],
            "observations": [],
        },
        "played_cards": {},
        "finalized": False,
    }


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True, sort_keys=True)
        f.write("\n")


def _append_unique(values: list[str], additions: list[str]) -> bool:
    existing = set(values)
    changed = False
    for item in additions:
        if item not in existing:
            values.append(item)
            existing.add(item)
            changed = True
    return changed


def _draft_seen_names(player_model: PlayerViewModel) -> list[str]:
    names: list[str] = []

    waiting_for = player_model.waitingFor
    if waiting_for is not None and waiting_for.cards:
        for card in waiting_for.cards:
            name = _card_name(card)
            if name:
                names.append(name)

    for card in player_model.draftedCards:
        name = _card_name(card)
        if name:
            names.append(name)

    return names


def _drafted_names(player_model: PlayerViewModel) -> list[str]:
    drafted: list[str] = []
    for card in player_model.draftedCards:
        name = _card_name(card)
        if name:
            drafted.append(name)
    return drafted


def _played_cards_by_player(player_model: PlayerViewModel) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for player in player_model.players:
        names: list[str] = []
        for card in player.tableau:
            name = _card_name(card)
            if name:
                names.append(name)
        result[player.name] = names
    return result


def observe_player_model(player_model: PlayerViewModel) -> None:
    tracker_key = _tracker_key(player_model)
    if tracker_key is None:
        return

    state = _IN_MEMORY_STATE.setdefault(tracker_key, _empty_state())
    if state.get("finalized"):
        return

    game = player_model.game
    state["game_id"] = game.id or state.get("game_id", "")
    state["player_id"] = player_model.id
    state["self_player"] = player_model.thisPlayer.name
    state["generation"] = game.generation

    draft_state = state.setdefault(
        "draft",
        {"seen_card_names": [], "drafted_card_names": [], "observations": []},
    )

    if _is_draft_prompt(player_model):
        seen_names = _draft_seen_names(player_model)
        drafted_names = _drafted_names(player_model)
        changed = False
        changed |= _append_unique(draft_state["seen_card_names"], seen_names)
        changed |= _append_unique(draft_state["drafted_card_names"], drafted_names)

        observation = {
            "generation": game.generation,
            "phase": game.phase,
            "seen_card_names": seen_names,
            "drafted_card_names": drafted_names,
        }
        observations: list[dict[str, Any]] = draft_state["observations"]
        if not observations or observations[-1] != observation:
            observations.append(observation)
            changed = True

    played_cards = _played_cards_by_player(player_model)
    if state.get("played_cards") != played_cards:
        state["played_cards"] = played_cards

    if game.phase == "end":
        final_path = _final_path_for(player_model)
        if final_path is None:
            return
        final_state = {
            "game_id": state["game_id"],
            "player_id": state["player_id"],
            "self_player": state["self_player"],
            "generation": state["generation"],
            "draft": draft_state,
            "played_cards": state["played_cards"],
        }
        _write_json(final_path, final_state)
        state["finalized"] = True
