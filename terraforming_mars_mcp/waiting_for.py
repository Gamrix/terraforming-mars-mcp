from __future__ import annotations

import json

from .api_response_models import PlayerViewModel as ApiPlayerViewModel
from .api_response_models import WaitingForInputModel as ApiWaitingForInputModel
from ._enums import InputType
from .card_info import DETAIL_LEVEL_FULL, _compact_cards


def _input_type_name(waiting_for: ApiWaitingForInputModel | None) -> str | None:
    if waiting_for is None:
        return None
    value = waiting_for.type
    try:
        return InputType(value).value
    except ValueError:
        return value


def _get_waiting_for_model(player_model: ApiPlayerViewModel) -> ApiWaitingForInputModel | None:
    return player_model.waitingFor


def _normalize_or_sub_response(
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


def _find_or_option_index(
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


def _normalize_waiting_for(
    waiting_for: ApiWaitingForInputModel | None,
    depth: int = 0,
    detail_level: str = DETAIL_LEVEL_FULL,
) -> dict[str, object] | None:
    if waiting_for is None:
        return None

    wf = waiting_for

    normalized: dict[str, object] = {
        "input_type": _input_type_name(wf),
        "title": wf.title,
        "button_label": wf.buttonLabel,
    }

    if wf.warning is not None:
        normalized["warning"] = wf.warning
    if wf.warnings:
        normalized["warnings"] = wf.warnings

    if wf.initialIdx is not None:
        normalized["initial_index"] = wf.initialIdx

    if wf.min is not None or wf.max is not None:
        amount_range: dict[str, object] = {}
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

    if wf.include:
        normalized["include"] = wf.include

    if wf.cards is not None:
        normalized["cards"] = _compact_cards(wf.cards, detail_level=detail_level)
        card_selection: dict[str, object] = {}
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

    if wf.players:
        normalized["players"] = wf.players
    if wf.spaces:
        normalized["spaces"] = wf.spaces
    if wf.parties:
        normalized["parties"] = wf.parties
    if wf.globalEventNames:
        normalized["globalEventNames"] = wf.globalEventNames

    if wf.tokens:
        normalized["tokens"] = [
            token.model_dump(exclude_none=True) for token in wf.tokens
        ]

    if wf.coloniesModel is not None:
        normalized["colonies"] = [colony.name for colony in wf.coloniesModel]

    if wf.payProduction is not None:
        normalized["pay_production"] = wf.payProduction.model_dump(exclude_none=True)

    if wf.paymentOptions is not None:
        normalized["payment_options"] = wf.paymentOptions.model_dump(exclude_none=True)

    if wf.aresData is not None:
        ares_data = wf.aresData.model_dump(exclude_none=True)
        normalized["ares_data"] = ares_data.get("hazardData", ares_data)

    if wf.options is not None:
        if depth >= 2:
            normalized["options_count"] = len(wf.options)
        else:
            normalized_options: list[dict[str, object]] = []
            for idx, option in enumerate(wf.options):
                option_detail = _normalize_waiting_for(
                    option, depth + 1, detail_level=detail_level
                )
                option_payload: dict[str, object] = {
                    "index": idx,
                    "title": option.title,
                    "input_type": _input_type_name(option),
                }
                if wf.initialIdx is not None:
                    option_payload["is_initial"] = idx == wf.initialIdx
                if option_detail is not None:
                    for key, value in option_detail.items():
                        if key in ("input_type", "title"):
                            continue
                        option_payload[key] = value

                normalized_options.append(option_payload)

            normalized["options"] = normalized_options

    return normalized
