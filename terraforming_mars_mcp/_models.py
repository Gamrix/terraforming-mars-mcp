from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _parse_card_list(value: list[str] | str | None, field_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, list):
        parsed: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError(f"{field_name} must contain only strings")
            trimmed = item.strip()
            if trimmed:
                parsed.append(trimmed)
        return parsed
    raise ValueError(
        f"{field_name} must be a list of strings or a comma-separated string"
    )


CardListField = Annotated[
    list[str],
    BeforeValidator(lambda value, info: _parse_card_list(value, str(info.field_name))),
]


class PaymentPayloadModel(BaseModel):
    # extra="forbid" so a stale key (e.g. the game server's old `megaCredits`
    # spelling) fails loudly here instead of as an opaque HTTP 400.
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    megacredits: int = 0
    steel: int = 0
    titanium: int = 0
    heat: int = 0
    plants: int = 0
    microbes: int = 0
    floaters: int = 0
    luna_archives_science: int = Field(default=0, alias="lunaArchivesScience")
    spire_science: int = Field(default=0, alias="spireScience")
    seeds: int = 0
    aurorai_data: int = Field(default=0, alias="auroraiData")
    graphene: int = 0
    kuiper_asteroids: int = Field(default=0, alias="kuiperAsteroids")


class UnitsPayloadModel(BaseModel):
    megacredits: int = 0
    steel: int = 0
    titanium: int = 0
    plants: int = 0
    energy: int = 0
    heat: int = 0


class InitialCardsSelectionModel(BaseModel):
    corporation_card: str | None = None
    project_cards: CardListField
    prelude_cards: CardListField = Field(default_factory=list)
    ceo_cards: CardListField = Field(default_factory=list)


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
        ).model_dump(by_alias=True)
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
