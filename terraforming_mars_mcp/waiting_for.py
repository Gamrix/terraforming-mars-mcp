from __future__ import annotations

import json

from .api_response_models import (
    MessageModel,
    WaitingForInputModel as ApiWaitingForInputModel,
)
from ._enums import DetailLevel, InputType, strip_empty
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
    value: str | dict[str, object] | None,
) -> dict[str, object]:
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


_PASS_TITLES = {"pass for this generation", "end turn"}


def find_pass_option_index(
    waiting_for: ApiWaitingForInputModel,
) -> int | None:
    """Return the index of the pass/end-turn option, or ``None`` if absent."""
    options = waiting_for.options
    if options is None:
        return None
    for idx, option in enumerate(options):
        if option.warnings and "pass" in option.warnings:
            return idx
        title_text = title_to_text(option.title).lower()
        if title_text in _PASS_TITLES:
            return idx
    return None


def find_or_option_index(
    waiting_for: ApiWaitingForInputModel, expected_type: str
) -> int:
    options = waiting_for.options
    if options is None:
        raise RuntimeError("Current waitingFor has no options for an 'or' prompt")

    initial_idx = waiting_for.initialIdx
    if isinstance(initial_idx, int) and 0 <= initial_idx < len(options):
        initial_option = options[initial_idx]
        if initial_option.type == expected_type:
            return initial_idx

    for idx, option in enumerate(options):
        if option.type == expected_type:
            return idx

    raise RuntimeError(
        f"No outer 'or' option of type '{expected_type}' is currently available"
    )


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
            "initial_index": wf.initialIdx or None,
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
        if "sell patents" in title_to_text(wf.title).lower():
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
            for idx, option in enumerate(wf.options):
                option_detail = normalize_waiting_for(
                    option,
                    depth + 1,
                    detail_level=detail_level,
                    generation=generation,
                    auto_response=auto_response,
                )
                input_type = input_type_name(option)
                option_payload: dict[str, object] = {
                    "index": idx,
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

                if "sell patents" in title_to_text(option.title).lower():
                    option_payload.pop("cards", None)

                normalized_options.append(option_payload)

            normalized["options"] = normalized_options

    return normalized
