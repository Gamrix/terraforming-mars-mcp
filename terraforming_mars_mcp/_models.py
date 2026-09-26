from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PaymentPayloadModel(BaseModel):
    # Field names match the game server's `Payment` keys; extra="forbid" so a
    # stale key (e.g. the old `megaCredits` spelling) fails loudly here instead of as an opaque HTTP 400.
    model_config = ConfigDict(extra="forbid")

    megacredits: int = 0
    steel: int = 0
    titanium: int = 0
    heat: int = 0
    plants: int = 0
    microbes: int = 0
    floaters: int = 0
    lunaArchivesScience: int = 0
    spireScience: int = 0
    seeds: int = 0
    auroraiData: int = 0
    graphene: int = 0
    kuiperAsteroids: int = 0


class UnitsPayloadModel(BaseModel):
    megacredits: int = 0
    steel: int = 0
    titanium: int = 0
    plants: int = 0
    energy: int = 0
    heat: int = 0


class InitialCardsSelectionModel(BaseModel):
    corporation_card: str | None = None
    project_cards: list[str]
    prelude_cards: list[str] = Field(default_factory=list)
    ceo_cards: list[str] = Field(default_factory=list)


def normalize_raw_input_entity(
    entity: dict[str, object],
) -> dict[str, object]:
    """Fill and validate payment payloads, recursing into or/and envelopes.

    The game server rejects partial payment objects, so every nested
    `projectCard`/`payment` response must carry the full payment shape.
    """
    normalized = dict(entity)
    entity_type = normalized.get("type")

    if isinstance(entity_type, str) and entity_type in {"payment", "projectCard"}:
        payment = normalized.get("payment")
        normalized["payment"] = PaymentPayloadModel.model_validate(
            payment if isinstance(payment, dict) else {}
        ).model_dump()
    elif entity_type == "or":
        response = normalized.get("response")
        if isinstance(response, dict):
            normalized["response"] = normalize_raw_input_entity(response)
    elif entity_type in {"and", "initialCards"}:
        responses = normalized.get("responses")
        if isinstance(responses, list):
            normalized["responses"] = [
                normalize_raw_input_entity(item) if isinstance(item, dict) else item
                for item in responses
            ]
    return normalized
