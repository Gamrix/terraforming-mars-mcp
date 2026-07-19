from __future__ import annotations

import re
from typing import cast

from ._enums import DetailLevel, InputType, strip_empty
from ._models import normalize_raw_input_entity
from .api_response_models import (
    JsonValue,
    MessageModel,
)
from .api_response_models import (
    WaitingForInputModel as ApiWaitingForInputModel,
)
from .card_info import compact_cards


def input_type_name(waiting_for: ApiWaitingForInputModel | None) -> str | None:
    if waiting_for is None:
        return None
    value = waiting_for.type
    try:
        return InputType(value).value
    except ValueError:
        return value


def normalize_or_sub_response(
    value: dict[str, object] | None,
) -> dict[str, object]:
    if value is None:
        return {"type": "option"}
    if "type" not in value:
        return {"type": "option", **value}
    return value


def title_to_text(title: str | MessageModel) -> str:
    if isinstance(title, str):
        return title
    return title.message


def _is_undo_option(
    *,
    input_type: str | None,
    title: str | MessageModel,
    warnings: list[str] | None,
) -> bool:
    if warnings and "undoBestEffort" in warnings:
        return True
    title_text = title_to_text(title).lower()
    return input_type == InputType.SELECT_OPTION.value and "undo" in title_text


def _is_sell_patents(title: str | MessageModel) -> bool:
    """The sell-patents card list duplicates the hand, so it is omitted."""
    return "sell patents" in title_to_text(title).lower()


def _should_hide_option(
    option: ApiWaitingForInputModel,
    option_detail: dict[str, object] | None,
    input_type: str | None,
) -> bool:
    """Hide options that are noise for agents: undo, learner-mode-only
    standard projects, and options whose cards all got filtered as disabled."""
    if option_detail is None:
        return _is_undo_option(input_type=input_type, title=option.title, warnings=None)
    raw_warnings = option_detail.get("warnings")
    warnings = (
        [w for w in raw_warnings if isinstance(w, str)]
        if isinstance(raw_warnings, list)
        else None
    )
    if _is_undo_option(input_type=input_type, title=option.title, warnings=warnings):
        return True
    card_sel = option_detail.get("card_selection")
    if isinstance(card_sel, dict) and card_sel.get("show_only_in_learner_mode"):
        return True
    cards = option_detail.get("cards")
    return isinstance(cards, list) and len(cards) == 0


def find_pass_option_index(
    waiting_for: ApiWaitingForInputModel,
) -> int | None:
    """Return the index of the pass-for-generation option, or ``None``.

    "End Turn" is never matched — clicking it merely yields the turn and the
    player gets prompted again.
    """
    options = waiting_for.options
    if options is None:
        return None
    for idx, option in enumerate(options):
        if option.warnings and "pass" in option.warnings:
            return idx
        if title_to_text(option.title).lower() == "pass for this generation":
            return idx
    return None


def _option_card_names(option: ApiWaitingForInputModel) -> list[str]:
    return [card if isinstance(card, str) else card.name for card in option.cards or []]


_TEMPLATE_PLACEHOLDER = re.compile(r"\$\{\d+\}")


def _normalize_title(text: str) -> str:
    return " ".join(_TEMPLATE_PLACEHOLDER.sub(" ", text).lower().split())


def find_or_option_index_by_name(
    waiting_for: ApiWaitingForInputModel, name: str
) -> int:
    """Resolve an 'or' option by its title (or a card it offers), not index.

    Titles are matched case-insensitively with ``${n}`` template placeholders
    stripped (e.g. "Fund an award (${0} M€)" matches "fund an award").
    """
    options = waiting_for.options
    if options is None:
        raise RuntimeError("Current waitingFor has no options for an 'or' prompt")

    query = _normalize_title(name)
    if not query:
        raise ValueError("Option name must be non-empty")
    titles = [_normalize_title(title_to_text(option.title)) for option in options]

    exact = [idx for idx, title in enumerate(titles) if title == query]
    if len(exact) == 1:
        return exact[0]
    partial = [
        idx
        for idx, title in enumerate(titles)
        if title and (query in title or title in query)
    ]
    if len(partial) == 1:
        return partial[0]
    by_card = [
        idx
        for idx, option in enumerate(options)
        if any(query == card.lower() for card in _option_card_names(option))
    ]
    if len(by_card) == 1:
        return by_card[0]
    raise RuntimeError(
        f"Cannot uniquely resolve or-option named '{name}'. Available options: {titles}"
    )


def _find_branch_index(
    waiting_for: ApiWaitingForInputModel,
    expected_type: str,
    card_name: str | None,
) -> int:
    """Pick the `or` branch matching a raw inner-type action."""
    options = waiting_for.options
    if options is None:
        raise RuntimeError("Current waitingFor has no options for an 'or' prompt")

    candidates = [
        idx for idx, option in enumerate(options) if option.type == expected_type
    ]
    if not candidates:
        raise RuntimeError(
            f"No outer 'or' option of type '{expected_type}' is currently available"
        )

    # Several branches can share a type (e.g. "Play project card" and
    # "Standard projects" are both projectCard) — pick the branch that
    # actually lists the requested card.
    if card_name is not None and len(candidates) > 1:
        for idx in candidates:
            if card_name in _option_card_names(options[idx]):
                return idx

    initial_idx = waiting_for.initialIdx
    if isinstance(initial_idx, int) and initial_idx in candidates:
        return initial_idx
    return candidates[0]


def resolve_action_for_prompt(
    action: dict[str, object],
    waiting_for: ApiWaitingForInputModel | None,
) -> dict[str, object]:
    """Resolve a raw InputResponse against the live prompt.

    `or` envelopes address their option by ``"name"`` (title or offered card);
    the matching index is filled in, recursively for nested menus, so callers
    are immune to option reordering. Raw inner-type actions (`projectCard`,
    `space`, `card`, `option`, ...) submitted against an `or` prompt are
    wrapped into the matching branch — chosen by card name for projectCard,
    then by type with ``initialIdx`` preference. Everything else passes
    through unchanged.
    """
    prompt = (
        waiting_for
        if waiting_for is not None and waiting_for.type == InputType.OR_OPTIONS.value
        else None
    )

    action_type = action.get("type")
    if action_type != InputType.OR_OPTIONS.value:
        if prompt is None or not isinstance(action_type, str):
            return action
        card = action.get("card")
        index = _find_branch_index(
            prompt, action_type, card if isinstance(card, str) else None
        )
        return {"type": "or", "index": index, "response": cast(JsonValue, action)}

    resolved = dict(action)
    if "index" in resolved:
        raise ValueError("'or' actions are addressed by 'name', not 'index'")
    name = resolved.pop("name", None)
    if name is None:
        raise ValueError("'or' action requires 'name'")
    if prompt is None:
        raise RuntimeError(
            "Current prompt is not an 'or'; cannot resolve option by name"
        )
    index = find_or_option_index_by_name(prompt, str(name))
    resolved["index"] = index

    options = prompt.options
    response = resolved.get("response")
    if isinstance(response, dict) and options and 0 <= index < len(options):
        resolved["response"] = cast(
            JsonValue, resolve_action_for_prompt(dict(response), options[index])
        )
    return resolved


def prepare_action(
    action: dict[str, object],
    waiting_for: ApiWaitingForInputModel | None,
) -> dict[str, object]:
    """Full submission prep: fill payment defaults, then resolve to the prompt."""
    return resolve_action_for_prompt(normalize_raw_input_entity(action), waiting_for)


def normalize_waiting_for(
    waiting_for: ApiWaitingForInputModel | None,
    depth: int = 0,
    detail_level: DetailLevel = DetailLevel.FULL,
    generation: int | None = None,
    auto_response: bool = False,
) -> dict[str, object] | None:
    if waiting_for is None:
        return None

    wf = waiting_for

    normalized: dict[str, object] = strip_empty(
        {
            "input_type": input_type_name(wf),
            "title": title_to_text(wf.title),
            "warning": title_to_text(wf.warning) if wf.warning is not None else None,
            "warnings": wf.warnings,
            "amount": wf.amount,
            "count": wf.count,
            "include": wf.include,
            "players": wf.players,
            "spaces": wf.spaces,
            "parties": wf.parties,
            "globalEventNames": wf.globalEventNames,
        }
    )

    if wf.cards is not None:
        is_blue_action = wf.selectBlueCardAction is True
        cards_list = compact_cards(
            wf.cards,
            detail_level=DetailLevel.MINIMAL if is_blue_action else detail_level,
            generation=generation,
            auto_response=auto_response,
        )
        # Filter out disabled cards; only include ones the player can use.
        cards_list = [c for c in cards_list if not c.get("disabled")]
        normalized["cards"] = cards_list
        card_selection: dict[str, object] = strip_empty(
            {
                "min": wf.min,
                "max": wf.max,
                "max_by_default": wf.maxByDefault,
                "select_blue_card_action": True if is_blue_action else None,
                "show_only_in_learner_mode": True
                if wf.showOnlyInLearnerMode is True
                else None,
                "show_owner": True if wf.showOwner is True else None,
            }
        )
        if card_selection:
            normalized["card_selection"] = card_selection
        if _is_sell_patents(wf.title):
            normalized.pop("cards", None)
    elif wf.min is not None or wf.max is not None:
        normalized["amount_range"] = strip_empty(
            {
                "min": wf.min,
                "max": wf.max,
                "max_by_default": wf.maxByDefault,
            }
        )

    if wf.tokens:
        normalized["tokens"] = [
            token.model_dump(exclude_none=True) for token in wf.tokens
        ]

    if wf.coloniesModel is not None:
        normalized["colonies"] = [colony.name for colony in wf.coloniesModel]

    if wf.payProduction is not None:
        normalized["pay_production"] = wf.payProduction.model_dump(exclude_none=True)

    if wf.paymentOptions is not None:
        payment_options = wf.paymentOptions.model_dump(exclude_none=True)
        if any(payment_options.values()):
            normalized["payment_options"] = payment_options

    if wf.aresData is not None:
        ares_data = wf.aresData.model_dump(exclude_none=True)
        normalized["ares_data"] = ares_data.get("hazardData", ares_data)

    if wf.options is not None:
        if depth >= 2:
            normalized["options_count"] = len(wf.options)
        else:
            normalized_options: list[dict[str, object]] = []
            for option in wf.options:
                option_detail = normalize_waiting_for(
                    option,
                    depth + 1,
                    detail_level=detail_level,
                    generation=generation,
                    auto_response=auto_response,
                )
                input_type = input_type_name(option)
                option_payload: dict[str, object] = {
                    "title": title_to_text(option.title),
                    "input_type": input_type,
                }
                if option_detail is not None:
                    for key, value in option_detail.items():
                        if key in ("input_type", "title"):
                            continue
                        option_payload[key] = value

                if _should_hide_option(option, option_detail, input_type):
                    continue

                if _is_sell_patents(option.title):
                    option_payload.pop("cards", None)

                normalized_options.append(option_payload)

            normalized["options"] = normalized_options

    return normalized
