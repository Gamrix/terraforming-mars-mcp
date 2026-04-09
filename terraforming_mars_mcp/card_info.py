from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ._enums import DetailLevel
from .api_response_models import (
    CardModel as ApiCardModel,
    PublicPlayerModel as ApiPublicPlayerModel,
)

_CARD_INFO_INDEX: dict[str, dict[str, object]] | None = None


class _CardDetailTracker:
    """Tracks per-card detail tier for auto-returned responses within a generation.

    Only applies to auto-returned data (after submitting an action). Proactive
    requests always get full detail regardless of this tracker.

    For auto-returned responses:
      1st appearance in generation → full detail (tags, requirements, effect_text, etc.)
      2nd+ appearance → name only, unless dynamic fields (warnings) changed
    Resets when generation changes or on explicit reset.
    """

    def __init__(self) -> None:
        self._generation: int | None = None
        self._seen: dict[str, dict[str, object]] = {}

    def should_send_details(
        self, card_name: str, generation: int, dynamic_fields: dict[str, object]
    ) -> bool:
        """Return True if this card should include details beyond just the name.

        Tracks cards by generation. Returns True on first appearance, and on
        subsequent appearances only if dynamic fields (warnings, etc.) changed.
        """
        if self._generation != generation:
            self._generation = generation
            self._seen.clear()
        prev = self._seen.get(card_name)
        self._seen[card_name] = dynamic_fields
        if prev is None:
            return True
        return prev != dynamic_fields

    def reset(self) -> None:
        self._generation = None
        self._seen.clear()


_CARD_TRACKER = _CardDetailTracker()


def _normalize_detail_level(detail_level: str | DetailLevel) -> DetailLevel:
    """Accept string or enum, return validated DetailLevel."""
    if isinstance(detail_level, DetailLevel):
        return detail_level
    normalized = str(detail_level).strip().lower()
    try:
        return DetailLevel(normalized)
    except ValueError:
        raise ValueError(
            f"detail_level must be one of {sorted(v.value for v in DetailLevel)}"
        ) from None


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
    raw_metadata = card.get("metadata")
    metadata = raw_metadata if isinstance(raw_metadata, dict) else None
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


def _all_effect_texts(info: dict[str, object]) -> list[str]:
    seen: set[str] = set()
    effect_texts: list[str] = []

    def add(value: object) -> None:
        if not isinstance(value, str):
            return
        normalized = value.strip()
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        effect_texts.append(normalized)

    description = info.get("description_text")
    add(description)
    if not isinstance(description, str) or not description.strip():
        add(info.get("on_play_effect_text"))

    for key in ("ongoing_effects", "activated_actions"):
        values = info.get(key)
        if not isinstance(values, list):
            continue
        for value in values:
            add(value)

    return effect_texts


def _best_effect_text(info: dict[str, object]) -> str | None:
    effect_texts = _all_effect_texts(info)
    return effect_texts[0] if effect_texts else None


def _compact_card(
    card: dict[str, object] | str | ApiCardModel,
    detail_level: str | DetailLevel = DetailLevel.FULL,
    generation: int | None = None,
    auto_response: bool = False,
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

    disabled = bool(card_model.isDisabled) if card_model else False

    # Disabled cards in auto-responses: just name + disabled flag.
    if disabled and auto_response:
        return {"name": card_name, "disabled": True}

    info = _card_info(card_name, include_play_details=True)
    base_cost = info.get("base_cost")
    discounted_cost = (
        card_model.calculatedCost
        if card_model and card_model.calculatedCost is not None
        else base_cost
    )
    warning = card_model.warning if card_model else None
    warnings = card_model.warnings if card_model else []
    resources = card_model.resources if card_model else None

    # Build dynamic fields dict for change detection in auto-response mode.
    dynamic_fields: dict[str, object] = {}
    if isinstance(warning, str) and warning.strip():
        dynamic_fields["warning"] = warning
    if isinstance(warnings, list) and warnings:
        dynamic_fields["warnings"] = tuple(warnings)
    if resources is not None:
        dynamic_fields["resources"] = resources

    # Auto-response caching: after first appearance in a generation,
    # return name-only unless dynamic fields changed.
    if auto_response and generation is not None:
        if not _CARD_TRACKER.should_send_details(card_name, generation, dynamic_fields):
            return {"name": card_name}

    # Build the payload with cost and dynamic fields.
    payload: dict[str, object] = {
        "name": card_name,
    }
    if disabled:
        payload["disabled"] = True
    cost = base_cost if base_cost is not None else discounted_cost
    if cost is not None:
        payload["cost"] = cost
    if discounted_cost is not None and discounted_cost != cost:
        payload["discounted_cost"] = discounted_cost
    if isinstance(warning, str) and warning.strip():
        payload["warning"] = warning
    if isinstance(warnings, list) and warnings:
        payload["warnings"] = warnings
    if resources is not None and resources != 0:
        payload["resources"] = resources
    vp = info.get("vp")
    if vp is not None:
        payload["vp"] = vp

    # Minimal detail (e.g. blue card actions): name + dynamic fields only.
    if normalized_detail_level == DetailLevel.MINIMAL:
        return payload

    # Full detail: include tags, requirements, and effect text.
    if normalized_detail_level == DetailLevel.FULL:
        tags = info.get("tags")
        if isinstance(tags, list) and tags:
            payload["tags"] = tags

        play_requirements_text = info.get("play_requirements_text")
        if isinstance(play_requirements_text, str) and play_requirements_text.strip():
            payload["play_requirements_text"] = play_requirements_text

        effect_texts = _all_effect_texts(info)
        # Strip duplicate requirement text from effect_texts[0].
        if (
            isinstance(play_requirements_text, str)
            and play_requirements_text.strip()
            and effect_texts
        ):
            req = play_requirements_text.strip()
            first = effect_texts[0]
            if first.startswith(req):
                stripped = first[len(req) :].strip()
                if stripped:
                    effect_texts[0] = stripped
                else:
                    effect_texts = effect_texts[1:]
        if effect_texts:
            payload["effect_texts"] = effect_texts

    return payload


def _compact_cards(
    cards: list[Any],
    detail_level: str | DetailLevel = DetailLevel.FULL,
    generation: int | None = None,
    auto_response: bool = False,
) -> list[dict[str, object]]:
    """Compact a list of cards with detail level appropriate to the call context.

    Proactive requests (auto_response=False): always return full detail per
    detail_level — the agent explicitly asked for this data.

    Auto-returned responses (auto_response=True): after submitting an action,
    the server returns game state automatically. To reduce noise:
      - 1st appearance of a card in a generation → full detail
      - 2nd+ appearance → name only (e.g. {"name": "Aquifer Pumping"}),
        unless dynamic fields (warnings, resources) changed since last seen

    Disabled cards in auto-responses return just {"name": ..., "disabled": True}.
    In proactive requests, disabled cards return full details with disabled flag.
    """
    compact_cards: list[dict[str, object]] = []
    for card in cards:
        compact = _compact_card(
            card,
            detail_level=detail_level,
            generation=generation,
            auto_response=auto_response,
        )
        if compact:
            compact_cards.append(compact)
    return compact_cards


def _ensure_player_model(
    player: ApiPublicPlayerModel | dict[str, object],
) -> ApiPublicPlayerModel:
    if isinstance(player, ApiPublicPlayerModel):
        return player
    return ApiPublicPlayerModel.model_validate(player)


def _extract_played_cards(
    player: ApiPublicPlayerModel | dict[str, object], include_play_details: bool = False
) -> list[dict[str, object]]:
    parsed_player = _ensure_player_model(player)
    return [
        _compact_card(card, detail_level=DetailLevel.FULL, auto_response=False)
        for card in parsed_player.tableau
    ]


def _extract_played_card_effects_and_actions(
    player: ApiPublicPlayerModel | dict[str, object],
) -> list[dict[str, object]]:
    parsed_player = _ensure_player_model(player)
    summaries: list[dict[str, object]] = []

    def _normalized_texts(values: object) -> list[str]:
        if not isinstance(values, list):
            return []
        texts: list[str] = []
        for value in values:
            if not isinstance(value, str):
                continue
            normalized = value.strip()
            if normalized:
                texts.append(normalized)
        return texts

    for card in parsed_player.tableau:
        info = _card_info(card.name, include_play_details=True)
        effect_texts = _normalized_texts(info.get("ongoing_effects"))
        action_texts = _normalized_texts(info.get("activated_actions"))
        if not effect_texts and not action_texts:
            continue

        summary: dict[str, object] = {"name": card.name}
        if effect_texts:
            summary["effect_texts"] = effect_texts
        if action_texts:
            summary["action_texts"] = action_texts
        summaries.append(summary)

    return summaries
