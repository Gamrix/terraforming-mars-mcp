from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TMBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class CardModel(TMBaseModel):
    name: str
    resources: int | None = None
    calculatedCost: int | None = None
    isDisabled: bool | None = None
    warnings: list[Any] | None = None
    warning: str | None = None
    cloneTag: str | None = None


class ColonyInputModel(TMBaseModel):
    name: str


class ClaimedTokenModel(TMBaseModel):
    # Underworld token payload shape can vary by expansion/version.
    pass


class WaitingForInputModel(TMBaseModel):
    type: str
    title: Any
    warning: Any | None = None
    warnings: list[Any] | None = None
    buttonLabel: str

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
    color: str
    score: int
    claimable: bool | None = None


class ClaimedMilestoneModel(TMBaseModel):
    name: str
    playerName: str | None = None
    color: str | None = None
    scores: list[MilestoneScoreModel] = Field(default_factory=list)


class AwardScoreModel(TMBaseModel):
    color: str
    score: int


class FundedAwardModel(TMBaseModel):
    name: str
    playerName: str | None = None
    color: str | None = None
    scores: list[AwardScoreModel] = Field(default_factory=list)


class SpaceModel(TMBaseModel):
    id: str
    x: int
    y: int
    spaceType: str
    bonus: list[int]
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
    phase: str
    generation: int
    temperature: int
    oxygenLevel: int
    oceans: int
    venusScaleLevel: int
    isTerraformed: bool
    gameAge: int = 0
    undoCount: int = 0
    passedPlayers: list[str] = Field(default_factory=list)
    spaces: list[SpaceModel] = Field(default_factory=list)
    milestones: list[ClaimedMilestoneModel] = Field(default_factory=list)
    awards: list[FundedAwardModel] = Field(default_factory=list)


class PublicPlayerModel(TMBaseModel):
    name: str
    color: str
    isActive: bool

    terraformRating: int = 0
    megaCredits: int = 0
    steel: int = 0
    titanium: int = 0
    plants: int = 0
    energy: int = 0
    heat: int = 0

    megaCreditProduction: int = 0
    steelProduction: int = 0
    titaniumProduction: int = 0
    plantProduction: int = 0
    energyProduction: int = 0
    heatProduction: int = 0

    cardsInHandNbr: int = 0
    actionsThisGeneration: list[str] = Field(default_factory=list)
    tableau: list[CardModel] = Field(default_factory=list)


class PlayerViewModel(TMBaseModel):
    id: str
    game: GameModel
    players: list[PublicPlayerModel]
    thisPlayer: PublicPlayerModel
    waitingFor: WaitingForInputModel | None = None
    cardsInHand: list[CardModel] = Field(default_factory=list)


class WaitingForStatusModel(TMBaseModel):
    result: str
    waitingFor: list[str]


class GameLogEntryModel(TMBaseModel):
    timestamp: int
    message: str
    data: list[Any]
    type: Any | None = None
    playerId: Any | None = None
