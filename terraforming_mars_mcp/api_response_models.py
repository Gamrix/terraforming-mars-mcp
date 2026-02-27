from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field


class TMBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow")


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

WarningLiteral: TypeAlias = Literal[
    "pass",
    "undoBestEffort",
    "maxtemp",
    "maxoxygen",
    "maxoceans",
    "maxvenus",
    "maxHabitatRate",
    "maxMiningRate",
    "maxLogisticsRate",
    "decreaseOwnProduction",
    "removeOwnPlants",
    "buildOnLuna",
    "preludeFizzle",
    "deckTooSmall",
    "cannotAffordBoardOfDirectors",
    "marsIsTerraformed",
    "ineffectiveDoubleDown",
    "noMatchingCards",
    "unusableEventsForAstraMechanica",
    "noEffect",
    "selfTarget",
    "pharmacyUnion",
    "kaguyaTech",
    "underworldtokendiscard",
]

SpaceHighlightLiteral: TypeAlias = Literal["noctis", "volcanic"]

UndergroundResourceTokenLiteral: TypeAlias = Literal[
    "data1pertemp",
    "mcprod1pertemp",
    "microbe1pertemp",
    "microbe2pertemp",
    "plant2pertemp",
    "steel2pertemp",
    "titanium1pertemp",
    "oceanrequirementmod",
    "oxygenrequirementmod",
    "temprequirementmod",
    "nothing",
    "card1",
    "card2",
    "corruption1",
    "corruption2",
    "data1",
    "data2",
    "data3",
    "steel2plant",
    "steel2",
    "steel1production",
    "titanium2",
    "titanium1production",
    "plant2",
    "plant3",
    "plant1production",
    "titaniumandplant",
    "energy2",
    "energy1production",
    "heat2production",
    "microbe1",
    "microbe2",
    "tr",
    "ocean",
    "sciencetag",
    "planttag",
    "place6mc",
    "anyresource1",
]

LogMessageTypeLiteral: TypeAlias = Literal[0, 1]


class LogMessageDataAttrsModel(TMBaseModel):
    tags: bool | None = None
    cost: bool | None = None


class LogMessageDataModel(TMBaseModel):
    type: int | str
    value: JsonScalar
    attrs: LogMessageDataAttrsModel | None = None


class MessageModel(TMBaseModel):
    message: str
    data: list[LogMessageDataModel] = Field(default_factory=list)


class UnitsModel(TMBaseModel):
    megacredits: int = 0
    steel: int = 0
    titanium: int = 0
    plants: int = 0
    energy: int = 0
    heat: int = 0


class PayProductionModel(TMBaseModel):
    cost: int
    units: UnitsModel


class PaymentOptionsModel(TMBaseModel):
    heat: bool | None = None
    steel: bool | None = None
    titanium: bool | None = None
    plants: bool | None = None
    microbes: bool | None = None
    floaters: bool | None = None
    lunaArchivesScience: bool | None = None
    spireScience: bool | None = None
    seeds: bool | None = None
    auroraiData: bool | None = None
    graphene: bool | None = None
    kuiperAsteroids: bool | None = None
    lunaTradeFederationTitanium: bool | None = None


class HazardConstraintModel(TMBaseModel):
    threshold: int
    available: bool


class MilestoneCountModel(TMBaseModel):
    id: str
    networkerCount: int
    purifierCount: int


class AresDataModel(TMBaseModel):
    includeHazards: bool | None = None
    hazardData: dict[str, HazardConstraintModel] | None = None
    milestoneResults: list[MilestoneCountModel] | None = None


class CardModel(TMBaseModel):
    name: str
    resources: int | None = None
    calculatedCost: int | None = None
    isDisabled: bool | None = None
    warnings: list[WarningLiteral] | None = None
    warning: str | None = None
    cloneTag: str | None = None


class ColonyInputModel(TMBaseModel):
    name: str


class ClaimedTokenModel(TMBaseModel):
    token: UndergroundResourceTokenLiteral | None = None
    shelter: bool | None = None
    active: bool | None = None
    id: int | None = None
    label: str | None = None


class WaitingForInputModel(TMBaseModel):
    type: str
    title: str | MessageModel
    warning: str | MessageModel | None = None
    warnings: list[WarningLiteral] | None = None
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
    payProduction: PayProductionModel | None = None
    paymentOptions: PaymentOptionsModel | None = None
    aresData: AresDataModel | None = None
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
    highlight: SpaceHighlightLiteral | None = None
    rotated: bool | None = None
    gagarin: int | None = None
    cathedral: bool | None = None
    nomads: bool | None = None
    coOwner: str | None = None
    undergroundResource: UndergroundResourceTokenLiteral | None = None
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
    result: Literal["GO", "REFRESH", "WAIT"]
    waitingFor: list[str]


class GameLogEntryModel(TMBaseModel):
    timestamp: int
    message: str
    data: list[LogMessageDataModel]
    type: LogMessageTypeLiteral | None = None
    playerId: str | None = None
