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
    BeforeValidator(
        lambda value, info: _parse_card_list(value, str(info.field_name))
    ),
]


class PaymentPayloadModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    mega_credits: int = Field(default=0, alias="megaCredits")
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


class InitialCardsSelectionModel(BaseModel):
    corporation_card: str | None = None
    project_cards: CardListField
    prelude_cards: CardListField = Field(default_factory=list)
    ceo_cards: CardListField = Field(default_factory=list)


class RawInputEntityRequest(BaseModel):
    entity_json: str


def _normalize_raw_input_entity(
    entity: dict[str, object],
) -> dict[str, object]:
    normalized = dict(entity)
    entity_type = normalized.get("type")

    if isinstance(entity_type, str) and entity_type in {"payment", "projectCard"}:
        if "payment" not in normalized:
            normalized["payment"] = PaymentPayloadModel().model_dump(by_alias=True)
        else:
            payment = normalized["payment"]
            if isinstance(payment, dict):
                normalized["payment"] = PaymentPayloadModel.model_validate(
                    payment
                ).model_dump(by_alias=True)
    return normalized
