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


def _card_name(card: CardModel | str) -> str | None:
    if isinstance(card, str):
        return card.strip() or None
    return card.name.strip() or None


def _append_unique(values: list[str], additions: list[str]) -> bool:
    existing = set(values)
    changed = False
    for item in additions:
        if item not in existing:
            values.append(item)
            existing.add(item)
            changed = True
    return changed


def observe_player_model(player_model: PlayerViewModel) -> None:
    game_id = player_model.game.id
    player_id = player_model.id
    if not game_id or not player_id:
        return
    tracker_key = f"{game_id}:{player_id}"

    state = _IN_MEMORY_STATE.setdefault(
        tracker_key,
        {
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
        },
    )
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

    waiting_for = player_model.waitingFor
    is_draft = False
    if waiting_for is not None:
        title = waiting_for.title
        if isinstance(title, str):
            title_text = title
        else:
            title_text = title.message
        is_draft = any(pattern.search(title_text) for pattern in _DRAFT_TITLE_PATTERNS)

    if is_draft:
        seen_names: list[str] = []
        if waiting_for is not None and waiting_for.cards:
            for card in waiting_for.cards:
                name = _card_name(card)
                if name:
                    seen_names.append(name)
        for card in player_model.draftedCards:
            name = _card_name(card)
            if name:
                seen_names.append(name)

        drafted_names: list[str] = []
        for card in player_model.draftedCards:
            name = _card_name(card)
            if name:
                drafted_names.append(name)

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

    played_cards: dict[str, list[str]] = {}
    for player in player_model.players:
        names: list[str] = []
        for card in player.tableau:
            name = _card_name(card)
            if name:
                names.append(name)
        played_cards[player.name] = names
    if state.get("played_cards") != played_cards:
        state["played_cards"] = played_cards

    if game.phase == "end":
        if not game_id:
            return
        date_slug = datetime.now().strftime("%Y_%m_%d")
        final_path = _REPO_OUTPUT_ROOT / date_slug / f"observed-cards-{game_id}.json"

        final_state = {
            "game_id": state["game_id"],
            "player_id": state["player_id"],
            "self_player": state["self_player"],
            "generation": state["generation"],
            "draft": draft_state,
            "played_cards": state["played_cards"],
        }
        final_path.parent.mkdir(parents=True, exist_ok=True)
        with final_path.open("w", encoding="utf-8") as f:
            json.dump(final_state, f, indent=2, ensure_ascii=True, sort_keys=True)
            f.write("\n")
        state["finalized"] = True
