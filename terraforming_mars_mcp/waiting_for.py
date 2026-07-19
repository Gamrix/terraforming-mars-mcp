from __future__ import annotations

import re
from typing import cast

from ._enums import DetailLevel, InputType, strip_empty
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


def find_or_option_index(
    waiting_for: ApiWaitingForInputModel,
    expected_type: str,
    card_name: str | None = None,
) -> int:
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


def resolve_or_action(
    action: dict[str, object],
    waiting_for: ApiWaitingForInputModel | None,
) -> dict[str, object]:
    """Fill in 'index' for 'or' envelopes addressed by option 'name'.

    Names are resolved against the live prompt (recursively for nested 'or'
    menus like milestone/award submenus), so callers are immune to option
    reordering. Actions that already carry an index pass through with any
    stray 'name' keys removed.
    """
    if action.get("type") != InputType.OR_OPTIONS.value:
        return action
    resolved = dict(action)
    name = resolved.pop("name", None)
    options = (
        getattr(waiting_for, "options", None)
        if getattr(waiting_for, "type", None) == InputType.OR_OPTIONS.value
        else None
    )

    index = resolved.get("index")
    if not isinstance(index, int):
        if name is None:
            raise ValueError("'or' action requires either 'index' or 'name'")
        if waiting_for is None or options is None:
            raise RuntimeError(
                "Current prompt is not an 'or'; cannot resolve option by name"
            )
        index = find_or_option_index_by_name(waiting_for, str(name))
        resolved["index"] = index

    response = resolved.get("response")
    if isinstance(response, dict) and options is not None and 0 <= index < len(options):
        resolved["response"] = cast(
            JsonValue, resolve_or_action(dict(response), options[index])
        )
    return resolved


def wrap_action_for_prompt(
    action: dict[str, object],
    waiting_for: ApiWaitingForInputModel | None,
) -> dict[str, object]:
    """Wrap a raw InputResponse in an `or` envelope if the current prompt is an `or`.

    The server only accepts an OrOptionsResponse when `waitingFor.type == "or"`.
    If the caller supplies a raw inner-type action (e.g. `projectCard`, `space`,
    `card`), locate the matching outer option and wrap accordingly. For
    projectCard actions the card name disambiguates between hand-card and
    standard-project branches. Actions already shaped as `or` or submitted
    against a non-`or` prompt pass through.
    """
    if waiting_for is None or waiting_for.type != InputType.OR_OPTIONS.value:
        return action
    action_type = action.get("type")
    if not isinstance(action_type, str) or action_type == InputType.OR_OPTIONS.value:
        return action
    card_name = action.get("card")
    option_index = find_or_option_index(
        waiting_for,
        action_type,
        card_name=card_name if isinstance(card_name, str) else None,
    )
    return {
        "type": "or",
        "index": option_index,
        "response": cast(JsonValue, action),
    }


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

                option_warnings: list[str] | None = None
                if option_detail is not None:
                    raw_warnings = option_detail.get("warnings")
                    if isinstance(raw_warnings, list):
                        option_warnings = [
                            w for w in raw_warnings if isinstance(w, str)
                        ]
                if _is_undo_option(
                    input_type=input_type,
                    title=option.title,
                    warnings=option_warnings,
                ):
                    continue

                # Skip learner-mode-only options (e.g. all-disabled standard projects).
                if option_detail is not None:
                    card_sel = option_detail.get("card_selection")
                    if isinstance(card_sel, dict) and card_sel.get(
                        "show_only_in_learner_mode"
                    ):
                        continue

                # Skip options whose cards are all empty after disabled filtering.
                if option_detail is not None:
                    option_cards = option_detail.get("cards")
                    if isinstance(option_cards, list) and len(option_cards) == 0:
                        continue

                if _is_sell_patents(option.title):
                    option_payload.pop("cards", None)

                normalized_options.append(option_payload)

            normalized["options"] = normalized_options

    return normalized
