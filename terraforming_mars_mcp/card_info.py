from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .api_response_models import (
    CardModel as ApiCardModel,
    PublicPlayerModel as ApiPublicPlayerModel,
)

DETAIL_LEVEL_FULL = "full"
DETAIL_LEVEL_MINIMAL = "minimal"
VALID_DETAIL_LEVELS = {DETAIL_LEVEL_FULL, DETAIL_LEVEL_MINIMAL}

_CARD_INFO_INDEX: dict[str, dict[str, object]] | None = None


def _normalize_detail_level(detail_level: str) -> str:
    normalized = str(detail_level).strip().lower()
    if normalized not in VALID_DETAIL_LEVELS:
        raise ValueError(f"detail_level must be one of {sorted(VALID_DETAIL_LEVELS)}")
    return normalized


def _load_card_info_index() -> dict[str, dict[str, object]]:
    global _CARD_INFO_INDEX
    if _CARD_INFO_INDEX is not None:
        return _CARD_INFO_INDEX

    cards_file = (
        Path(__file__).resolve().parents[1]
        / "submodules"
        / "tm-oss-server"
        / "src"
        / "genfiles"
        / "cards.json"
    )
    if not cards_file.exists():
        _CARD_INFO_INDEX = {}
        return _CARD_INFO_INDEX

    raw = json.loads(cards_file.read_text(encoding="utf-8"))
    index: dict[str, dict[str, object]] = {}
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


def _description_text(metadata: dict[str, object] | None) -> str | None:
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


def _split_requirement_and_effect(
    description: str | None,
) -> tuple[str | None, str | None]:
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
        tile = (
            next(iter(moon_obj), "tile")
            if isinstance(moon_obj, dict) and moon_obj
            else "tile"
        )
        if per != 1:
            return f"1 per {per} {tile} tiles on Moon"
        return f"1 per {tile} tile on Moon"
    return None


def _card_info(card_name: Any, include_play_details: bool = False) -> dict[str, object]:
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

    info: dict[str, object] = {
        "name": card_name,
        "tags": tags,
        "ongoing_effects": effects,
        "activated_actions": actions,
        "description_text": description,
        "vp": vp,
    }

    if include_play_details:
        req_text, on_play = _split_requirement_and_effect(description)
        requirements = (
            card.get("requirements")
            if isinstance(card.get("requirements"), list)
            else []
        )
        info.update(
            {
                "base_cost": card.get("cost"),
                "play_requirements": requirements,
                "play_requirements_text": req_text,
                "on_play_effect_text": on_play,
            }
        )
    return info


def _best_effect_text(info: dict[str, object]) -> str | None:
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


def _compact_card(
    card: dict[str, object] | str | ApiCardModel,
    detail_level: str = DETAIL_LEVEL_FULL,
) -> dict[str, object]:
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
    discounted_cost = (
        card_model.calculatedCost
        if card_model and card_model.calculatedCost is not None
        else base_cost
    )
    disabled = bool(card_model.isDisabled) if card_model else False
    warning = card_model.warning if card_model else None
    warnings = card_model.warnings if card_model else []
    resources = card_model.resources if card_model else None

    payload: dict[str, object] = {
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

        play_requirements = info.get("play_requirements")
        if isinstance(play_requirements, list) and play_requirements:
            payload["play_requirements"] = play_requirements

        play_requirements_text = info.get("play_requirements_text")
        if isinstance(play_requirements_text, str) and play_requirements_text.strip():
            payload["play_requirements_text"] = play_requirements_text

        effect_text = _best_effect_text(info)
        if isinstance(effect_text, str) and effect_text.strip():
            payload["effect_text"] = effect_text

    return payload


def _compact_cards(
    cards: list[Any],
    detail_level: str = DETAIL_LEVEL_FULL,
) -> list[dict[str, object]]:
    compact_cards: list[dict[str, object]] = []
    for card in cards:
        compact = _compact_card(card, detail_level=detail_level)
        if compact:
            compact_cards.append(compact)
    return compact_cards


def _extract_played_cards(
    player: ApiPublicPlayerModel | dict[str, object], include_play_details: bool = False
) -> list[dict[str, object]]:
    parsed_player = (
        player
        if isinstance(player, ApiPublicPlayerModel)
        else ApiPublicPlayerModel.model_validate(player)
    )
    tableau = parsed_player.tableau
    cards: list[dict[str, object]] = []
    if isinstance(tableau, list):
        for card in tableau:
            info = _card_info(card.name, include_play_details=include_play_details)
            payload: dict[str, object] = {
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
                discounted_cost = (
                    card.calculatedCost
                    if card.calculatedCost is not None
                    else base_cost
                )
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
