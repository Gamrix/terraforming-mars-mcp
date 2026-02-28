from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Literal, TypedDict

from .api_response_models import (
    GameModel as ApiGameModel,
    PlayerViewModel as ApiPlayerViewModel,
    PublicPlayerModel as ApiPublicPlayerModel,
)
from ._enums import _action_tools_for_input_type
from .card_info import DETAIL_LEVEL_FULL, _card_info, _normalize_detail_level
from .waiting_for import _input_type_name, _normalize_waiting_for

END_OF_GENERATION_PHASES = {"production", "solar", "intergeneration", "end"}

_LAST_OPPONENT_TABLEAU: dict[str, dict[str, Counter[str]]] = {}
# Tracks (generation, constants_dict) so we send full constants once per gen.
_LAST_GAME_CONSTANTS: dict[str, tuple[int, dict[str, object]]] = {}


@dataclass(frozen=True)
class _MilestonesAwardsSnapshot:
    generation: int
    claimed: frozenset[str]
    funded: frozenset[str]
    claimable: frozenset[tuple[str, str]]


@dataclass(frozen=True)
class _ProductionSummary:
    mc: int
    steel: int
    titanium: int
    plants: int
    energy: int
    heat: int

    def to_payload(self) -> dict[str, int]:
        return {
            "mc": self.mc,
            "steel": self.steel,
            "titanium": self.titanium,
            "plants": self.plants,
            "energy": self.energy,
            "heat": self.heat,
        }


@dataclass(frozen=True)
class _PlayerSummary:
    name: str
    color: str
    active: bool
    tr: int
    mc: int
    steel: int
    titanium: int
    plants: int
    energy: int
    heat: int
    prod: _ProductionSummary
    cards_in_hand_count: int
    actions_this_generation: list[str]

    def to_full_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "color": self.color,
            "active": self.active,
            "tr": self.tr,
            "mc": self.mc,
            "steel": self.steel,
            "titanium": self.titanium,
            "plants": self.plants,
            "energy": self.energy,
            "heat": self.heat,
            "prod": self.prod.to_payload(),
            "cards_in_hand_count": self.cards_in_hand_count,
            "actions_this_generation": list(self.actions_this_generation),
        }

    def to_minimal_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "color": self.color,
            "active": self.active,
            "tr": self.tr,
            "cards_in_hand_count": self.cards_in_hand_count,
        }


_LAST_MA_SNAPSHOT: dict[str, _MilestonesAwardsSnapshot] = {}


class _MilestoneScorePayload(TypedDict):
    color: str
    score: int
    claimable: bool


class _MilestonePayload(TypedDict):
    name: str
    status: Literal["claimed", "available"]
    owner_color: str | None
    owner_name: str | None
    scores: list[_MilestoneScorePayload]
    claimable_by: list[str]


class _AwardScorePayload(TypedDict):
    color: str
    score: int


class _AwardPayload(TypedDict):
    name: str
    status: Literal["funded", "unfunded"]
    funder_color: str | None
    funder_name: str | None
    scores: list[_AwardScorePayload]

_TILE_TYPE_LABELS = (
    "greenery",
    "ocean",
    "city",
    "capital",
    "commercial district",
    "ecological zone",
    "industrial center",
    "lava flows",
    "mining area",
    "mining rights",
    "mohole area",
    "natural preserve",
    "nuclear zone",
    "restricted area",
    "deimos down",
    "great dam",
    "magnetic field generators",
    "biofertilizer facility",
    "metallic asteroid",
    "solar farm",
    "ocean city",
    "ocean farm",
    "ocean sanctuary",
    "dust storm mild",
    "dust storm severe",
    "erosion mild",
    "erosion severe",
    "mining steel bonus",
    "mining titanium bonus",
    "moon mine",
    "moon habitat",
    "moon road",
    "luna trade station",
    "luna mining hub",
    "luna train station",
    "lunar mine urbanization",
    "wetlands",
    "red city",
    "martian nature wonders",
    "crashlanding",
    "mars nomads",
    "rey skywalker",
    "man made volcano",
    "new holland",
)


def _player_summary(player: ApiPublicPlayerModel) -> _PlayerSummary:
    return _PlayerSummary(
        name=player.name,
        color=player.color,
        active=player.isActive,
        tr=player.terraformRating,
        mc=player.megaCredits,
        steel=player.steel,
        titanium=player.titanium,
        plants=player.plants,
        energy=player.energy,
        heat=player.heat,
        prod=_ProductionSummary(
            mc=player.megaCreditProduction,
            steel=player.steelProduction,
            titanium=player.titaniumProduction,
            plants=player.plantProduction,
            energy=player.energyProduction,
            heat=player.heatProduction,
        ),
        cards_in_hand_count=player.cardsInHandNbr,
        actions_this_generation=list(player.actionsThisGeneration),
    )


def _summarize_players(
    player_model: ApiPlayerViewModel,
) -> tuple[_PlayerSummary, list[_PlayerSummary]]:
    this_player = player_model.thisPlayer
    player_color = this_player.color

    you: _PlayerSummary | None = None
    others: list[_PlayerSummary] = []
    for player in player_model.players:
        summary = _player_summary(player)
        if player.color == player_color:
            you = summary
        else:
            others.append(summary)

    return (you or _player_summary(this_player)), others


def _summarize_board(game: ApiGameModel) -> dict[str, object]:
    spaces = game.spaces
    occupied = 0
    by_tile: dict[str, int] = {}
    for space in spaces:
        tile_type = space.tileType
        if tile_type is not None:
            occupied += 1
            key = (
                _TILE_TYPE_LABELS[tile_type]
                if 0 <= tile_type < len(_TILE_TYPE_LABELS)
                else str(tile_type)
            )
            by_tile[key] = by_tile.get(key, 0) + 1
    return {
        "total_spaces": len(spaces),
        "occupied_spaces": occupied,
        "tile_counts": by_tile,
    }


def _summarize_milestones(game: ApiGameModel) -> list[_MilestonePayload]:
    summarized: list[_MilestonePayload] = []
    for milestone in game.milestones:
        owner_color = milestone.color
        owner_name = milestone.playerName
        status: Literal["claimed", "available"] = (
            "claimed" if owner_color or owner_name else "available"
        )

        scores: list[_MilestoneScorePayload] = []
        claimable_by: list[str] = []
        for score in milestone.scores or []:
            compact: _MilestoneScorePayload = {
                "color": score.color,
                "score": score.score,
                "claimable": score.claimable is True,
            }
            scores.append(compact)
            if score.claimable is True:
                claimable_by.append(score.color)

        summarized.append(
            {
                "name": milestone.name,
                "status": status,
                "owner_color": owner_color,
                "owner_name": owner_name,
                "scores": scores,
                "claimable_by": claimable_by,
            }
        )
    return summarized


def _summarize_awards(game: ApiGameModel) -> list[_AwardPayload]:
    summarized: list[_AwardPayload] = []
    for award in game.awards:
        funder_color = award.color
        funder_name = award.playerName
        status: Literal["funded", "unfunded"] = (
            "funded" if funder_color or funder_name else "unfunded"
        )

        scores: list[_AwardScorePayload] = []
        for score in award.scores or []:
            scores.append({"color": score.color, "score": score.score})

        summarized.append(
            {
                "name": award.name,
                "status": status,
                "funder_color": funder_color,
                "funder_name": funder_name,
                "scores": scores,
            }
        )
    return summarized


def _should_include_milestones_awards(
    game: ApiGameModel,
    milestones: list[_MilestonePayload],
    awards: list[_AwardPayload],
    player_id: str,
) -> bool:
    """Include milestones/awards once per generation or when a critical change occurs.

    Critical changes:
    - A milestone was newly claimed (status changed to 'claimed')
    - An award was newly funded (status changed to 'funded')
    - A player became newly claimable for a milestone
    - Generation changed (show once at start of each generation)
    - First call for this game (no previous snapshot)
    """
    game_id = game.id or ""
    ma_key = f"{game_id}:{player_id}"
    prev = _LAST_MA_SNAPSHOT.get(ma_key)

    claimed_set = frozenset(m["name"] for m in milestones if m["status"] == "claimed")
    funded_set = frozenset(a["name"] for a in awards if a["status"] == "funded")
    claimable_set = frozenset(
        (m["name"], c) for m in milestones for c in m.get("claimable_by", [])
    )
    generation = game.generation
    current = _MilestonesAwardsSnapshot(
        generation=generation,
        claimed=claimed_set,
        funded=funded_set,
        claimable=claimable_set,
    )

    include = False
    if prev is None:
        include = True
    elif prev.generation != generation:
        include = True
    elif prev.claimed != claimed_set:
        include = True
    elif prev.funded != funded_set:
        include = True
    elif prev.claimable != claimable_set:
        include = True

    _LAST_MA_SNAPSHOT[ma_key] = current
    return include


def _full_board_state(
    game: ApiGameModel, include_empty_spaces: bool = False
) -> dict[str, object]:
    mars_spaces: list[dict[str, object]] = []
    for space in game.spaces:
        if not include_empty_spaces and space.tileType is None:
            continue
        space_data: dict[str, object] = {
            "id": space.id,
            "x": space.x,
            "y": space.y,
            "space_type": space.spaceType,
        }
        if space.bonus:
            space_data["bonus"] = space.bonus
        if space.tileType is not None:
            tile_type = space.tileType
            space_data["tile_type"] = (
                _TILE_TYPE_LABELS[tile_type]
                if 0 <= tile_type < len(_TILE_TYPE_LABELS)
                else str(tile_type)
            )
        if space.color is not None:
            space_data["owner_color"] = space.color
        if space.coOwner is not None:
            space_data["co_owner_color"] = space.coOwner
        if space.highlight is not None:
            space_data["highlight"] = space.highlight
        if space.gagarin is not None:
            space_data["gagarin"] = space.gagarin
        if space.rotated is not None:
            space_data["rotated"] = space.rotated
        if space.cathedral is not None:
            space_data["cathedral"] = space.cathedral
        if space.nomads is not None:
            space_data["nomads"] = space.nomads
        if space.undergroundResource is not None:
            space_data["underground_resource"] = space.undergroundResource
        if space.excavator is not None:
            space_data["excavator"] = space.excavator
        mars_spaces.append(space_data)

    return {
        "game_id": game.id,
        "phase": game.phase,
        "generation": game.generation,
        "globals": {
            "temperature": game.temperature,
            "oxygen": game.oxygenLevel,
            "oceans": game.oceans,
            "venus": game.venusScaleLevel,
            "terraformed": game.isTerraformed,
        },
        "summary": _summarize_board(game),
        "spaces": mars_spaces,
    }


def _detect_new_opponent_cards(
    player_model: ApiPlayerViewModel,
) -> list[dict[str, object]]:
    game_id = player_model.game.id
    pid = player_model.id or ""
    if not isinstance(game_id, str) or not isinstance(pid, str):
        return []
    key = f"{game_id}:{pid}"

    this_color = player_model.thisPlayer.color
    players = player_model.players

    current: dict[str, Counter[str]] = {}
    for player in players:
        color = player.color
        if color == this_color:
            continue
        tableau = player.tableau or []
        names = [card.name for card in tableau]
        current[color] = Counter(names)

    previous = _LAST_OPPONENT_TABLEAU.get(key, {})
    events: list[dict[str, object]] = []
    for player in players:
        color = player.color
        if color == this_color:
            continue
        old_counts = previous.get(color, Counter())
        new_counts = current.get(color, Counter())
        delta = new_counts - old_counts
        for card_name, count in delta.items():
            for _ in range(count):
                info = _card_info(card_name, include_play_details=True)
                event: dict[str, object] = {
                    "player_name": player.name,
                    "player_color": color,
                    "card_name": card_name,
                    "tags": info.get("tags", []),
                    "ongoing_effects": info.get("ongoing_effects", []),
                    "activated_actions": info.get("activated_actions", []),
                    "play_requirements": info.get("play_requirements", []),
                    "play_requirements_text": info.get("play_requirements_text"),
                    "on_play_effect_text": info.get("on_play_effect_text"),
                    "cost": info.get("base_cost"),
                    "discounted_cost": info.get("base_cost"),
                }
                vp = info.get("vp")
                if vp is not None:
                    event["vp"] = vp
                events.append(event)

    _LAST_OPPONENT_TABLEAU[key] = current
    return events


def _build_agent_state(
    player_model: ApiPlayerViewModel,
    include_full_model: bool = False,
    include_board_state: bool = False,
    detail_level: str = DETAIL_LEVEL_FULL,
    base_url: str | None = None,
    player_id_fallback: str | None = None,
    auto_response: bool = False,
) -> dict[str, object]:
    game = player_model.game
    normalized_detail_level = _normalize_detail_level(detail_level)
    waiting_for = player_model.waitingFor
    input_type = _input_type_name(waiting_for)
    you, opponents = _summarize_players(player_model)

    phase = game.phase
    show_board = include_board_state or (
        normalized_detail_level == DETAIL_LEVEL_FULL
        and phase in END_OF_GENERATION_PHASES
    )

    generation = game.generation
    player_id = player_model.id or player_id_fallback or ""
    game_id = game.id or ""
    constants_key = f"{game_id}:{player_id}"

    # Build session and game constants, then check if they changed.
    session: dict[str, object] = {
        "player_id": player_id,
    }
    if normalized_detail_level == DETAIL_LEVEL_FULL and base_url is not None:
        session["base_url"] = base_url

    # Core game constants that rarely change mid-turn.
    game_constants: dict[str, object] = {
        "phase": game.phase,
        "generation": generation,
        "terraforming": {
            "temperature": game.temperature,
            "oxygen": game.oxygenLevel,
            "oceans": game.oceans,
            "venus": game.venusScaleLevel,
            "terraformed": game.isTerraformed,
        },
    }

    prev = _LAST_GAME_CONSTANTS.get(constants_key)
    prev_gen, prev_constants = prev if prev is not None else (None, None)
    # Send full constants on first call, generation change, or value change.
    constants_changed = (
        prev_gen != generation or prev_constants != game_constants
    )
    _LAST_GAME_CONSTANTS[constants_key] = (generation, game_constants)

    game_state: dict[str, object] = {
        "id": game_id,
        "game_age": game.gameAge,
        "undo_count": game.undoCount,
        "passed_players": game.passedPlayers,
    }

    if constants_changed:
        game_state.update(game_constants)
    else:
        # Only include generation (always useful context) when constants unchanged.
        game_state["generation"] = generation

    if normalized_detail_level == DETAIL_LEVEL_FULL:
        milestones = _summarize_milestones(game)
        awards = _summarize_awards(game)
        include_ma = _should_include_milestones_awards(
            game,
            milestones,
            awards,
            player_model.id,
        )
        if include_ma:
            game_state["milestones"] = milestones
            game_state["awards"] = awards
        else:
            game_state["milestones_changed"] = False
    if show_board:
        game_state["board"] = _summarize_board(game)
        game_state["board_visible"] = True
    elif normalized_detail_level == DETAIL_LEVEL_FULL:
        game_state["board"] = None
        game_state["board_visible"] = False

    if normalized_detail_level == DETAIL_LEVEL_FULL:
        opponents_state = [summary.to_full_payload() for summary in opponents]
        opponent_card_events = _detect_new_opponent_cards(player_model)
    else:
        opponents_state = [summary.to_minimal_payload() for summary in opponents]
        opponent_card_events = []

    result: dict[str, object] = {}
    # Omit session when constants haven't changed (agent already knows it).
    if constants_changed:
        result["session"] = session
    result["game"] = game_state
    result["you"] = you.to_full_payload()
    result["opponents"] = opponents_state
    result["waiting_for"] = _normalize_waiting_for(
        waiting_for,
        detail_level=normalized_detail_level,
        generation=generation,
        auto_response=auto_response,
    )
    result["suggested_tools"] = _action_tools_for_input_type(input_type)
    result["opponent_card_events"] = opponent_card_events

    if include_full_model:
        result["raw_player_model"] = player_model.model_dump(exclude_none=True)
    return result
