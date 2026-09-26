from __future__ import annotations

from enum import StrEnum
from typing import Any


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


def strip_empty(obj: Any) -> Any:
    """Recursively strip None values and empty lists from dicts.

    Leaves other falsy values (0, False, empty strings) untouched since they
    carry semantic meaning in game state payloads.
    """
    if isinstance(obj, dict):
        return {k: strip_empty(v) for k, v in obj.items() if v is not None and v != []}
    if isinstance(obj, list):
        return [strip_empty(item) for item in obj]
    return obj
