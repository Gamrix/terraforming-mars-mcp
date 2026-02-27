from __future__ import annotations

from enum import StrEnum


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
