from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class TMBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class CardModel(TMBaseModel):
    name: str | None = None
    resources: int | None = None
    calculatedCost: int | None = None
    isDisabled: bool | None = None
    warnings: list[Any] | None = None
    warning: str | None = None
    cloneTag: str | None = None


class ColonyInputModel(TMBaseModel):
    name: str | None = None


class ClaimedTokenModel(TMBaseModel):
    # Underworld token payload shape can vary by expansion/version.
    pass


class WaitingForInputModel(TMBaseModel):
    type: str | None = None
    title: Any | None = None
    warning: Any | None = None
    warnings: list[Any] | None = None
    buttonLabel: str | None = None

    min: int | None = None
    max: int | None = None
    maxByDefault: bool | None = None
    amount: int | None = None
    count: int | None = None
    initialIdx: int | None = None

    cards: list[CardModel | str] | None = None
    showOnlyInLearnerMode: bool | None = None
    selectBlueCardAction: bool | None = None
    showOwner: bool | None = None

    options: list["WaitingForInputModel"] | None = None

    players: list[str] | None = None
    spaces: list[str] | None = None
    parties: list[str] | None = None
    globalEventNames: list[str] | None = None
    include: list[str] | None = None

    coloniesModel: list[ColonyInputModel] | None = None
    payProduction: dict[str, Any] | None = None
    paymentOptions: dict[str, Any] | None = None
    aresData: dict[str, Any] | None = None
    tokens: list[ClaimedTokenModel] | None = None


WaitingForInputModel.model_rebuild()


class MilestoneScoreModel(TMBaseModel):
    color: str | None = None
    score: int | None = None
    claimable: bool | None = None


class ClaimedMilestoneModel(TMBaseModel):
    name: str | None = None
    playerName: str | None = None
    color: str | None = None
    scores: list[MilestoneScoreModel] | None = None


class AwardScoreModel(TMBaseModel):
    color: str | None = None
    score: int | None = None


class FundedAwardModel(TMBaseModel):
    name: str | None = None
    playerName: str | None = None
    color: str | None = None
    scores: list[AwardScoreModel] | None = None


class SpaceModel(TMBaseModel):
    id: str | None = None
    x: int | None = None
    y: int | None = None
    spaceType: str | None = None
    bonus: list[int] | None = None
    color: str | None = None
    tileType: int | None = None
    highlight: str | None = None
    rotated: bool | None = None
    gagarin: int | None = None
    cathedral: bool | None = None
    nomads: bool | None = None
    coOwner: str | None = None
    undergroundResource: Any | None = None
    excavator: str | None = None


class GameModel(TMBaseModel):
    id: str | None = None
    phase: str | None = None
    generation: int | None = None
    temperature: int | None = None
    oxygenLevel: int | None = None
    oceans: int | None = None
    venusScaleLevel: int | None = None
    isTerraformed: bool | None = None
    gameAge: int | None = None
    undoCount: int | None = None
    passedPlayers: list[str] | None = None
    spaces: list[SpaceModel] | None = None
    milestones: list[ClaimedMilestoneModel] | None = None
    awards: list[FundedAwardModel] | None = None


class PublicPlayerModel(TMBaseModel):
    name: str | None = None
    color: str | None = None
    isActive: bool | None = None

    terraformRating: int | None = None
    megaCredits: int | None = None
    steel: int | None = None
    titanium: int | None = None
    plants: int | None = None
    energy: int | None = None
    heat: int | None = None

    megaCreditProduction: int | None = None
    steelProduction: int | None = None
    titaniumProduction: int | None = None
    plantProduction: int | None = None
    energyProduction: int | None = None
    heatProduction: int | None = None

    cardsInHandNbr: int | None = None
    actionsThisGeneration: list[str] | None = None
    tableau: list[CardModel] | None = None


class PlayerViewModel(TMBaseModel):
    id: str | None = None
    game: GameModel | None = None
    players: list[PublicPlayerModel] | None = None
    thisPlayer: PublicPlayerModel | None = None
    waitingFor: WaitingForInputModel | None = None
    cardsInHand: list[CardModel] | None = None


class WaitingForStatusModel(TMBaseModel):
    result: str | None = None
    waitingFor: list[str] | None = None


class GameLogEntryModel(TMBaseModel):
    timestamp: Any | None = None
    message: str | None = None
    data: list[Any] | None = None
    type: Any | None = None
    playerId: Any | None = None
