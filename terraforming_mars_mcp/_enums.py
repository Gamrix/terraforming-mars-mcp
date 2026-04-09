from __future__ import annotations

from enum import StrEnum


class DetailLevel(StrEnum):
    FULL = "full"
    MINIMAL = "minimal"


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
    PASS_TURN = "pass_turn"


_INPUT_TYPE_TO_TOOL: dict[InputType, ToolName] = {
    InputType.AND_OPTIONS: ToolName.SUBMIT_AND_OPTIONS,
    InputType.OR_OPTIONS: ToolName.CHOOSE_OR_OPTION,
    InputType.SELECT_AMOUNT: ToolName.SELECT_AMOUNT,
    InputType.SELECT_CARD: ToolName.SELECT_CARDS,
    InputType.SELECT_DELEGATE: ToolName.SELECT_DELEGATE_TARGET,
    InputType.SELECT_PAYMENT: ToolName.PAY_FOR_ACTION,
    InputType.SELECT_PROJECT_CARD_TO_PLAY: ToolName.PAY_FOR_PROJECT_CARD,
    InputType.SELECT_INITIAL_CARDS: ToolName.SELECT_INITIAL_CARDS,
    InputType.SELECT_OPTION: ToolName.CONFIRM_OPTION,
    InputType.SELECT_PARTY: ToolName.SELECT_PARTY,
    InputType.SELECT_PLAYER: ToolName.SELECT_PLAYER,
    InputType.SELECT_SPACE: ToolName.SELECT_SPACE,
    InputType.SELECT_COLONY: ToolName.SELECT_COLONY,
    InputType.SELECT_PRODUCTION_TO_LOSE: ToolName.SELECT_PRODUCTION_TO_LOSE,
    InputType.SHIFT_ARES_GLOBAL_PARAMETERS: ToolName.SHIFT_ARES_GLOBAL_PARAMETERS,
    InputType.SELECT_GLOBAL_EVENT: ToolName.SELECT_GLOBAL_EVENT,
    InputType.SELECT_POLICY: ToolName.SELECT_POLICY,
    InputType.SELECT_RESOURCE: ToolName.SELECT_RESOURCE,
    InputType.SELECT_RESOURCES: ToolName.SELECT_RESOURCES,
    InputType.SELECT_CLAIMED_UNDERGROUND_TOKEN: ToolName.SELECT_CLAIMED_UNDERGROUND_TOKEN,
}


def _action_tools_for_input_type(input_type: str | None) -> list[str]:
    if input_type is None:
        return []
    try:
        tool = _INPUT_TYPE_TO_TOOL[InputType(input_type)]
    except (ValueError, KeyError):
        return [ToolName.SUBMIT_RAW_ENTITY.value]
    return [tool.value, ToolName.SUBMIT_RAW_ENTITY.value]
