from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .api_response_models import (
    ClaimedMilestoneModel as ApiClaimedMilestoneModel,
    FundedAwardModel as ApiFundedAwardModel,
    GameModel as ApiGameModel,
    PlayerViewModel as ApiPlayerViewModel,
    PublicPlayerModel as ApiPublicPlayerModel,
    SpaceModel as ApiSpaceModel,
)
from ._enums import _action_tools_for_input_type
from .card_info import DETAIL_LEVEL_FULL, _card_info, _normalize_detail_level
from .waiting_for import (
    _get_waiting_for_model,
    _input_type_name,
    _normalize_waiting_for,
)

END_OF_GENERATION_PHASES = {"production", "solar", "intergeneration", "end"}

_LAST_OPPONENT_TABLEAU: dict[str, dict[str, Counter[str]]] = {}


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


def _tile_type_name(tile_type: int) -> str:
    if 0 <= tile_type < len(_TILE_TYPE_LABELS):
        return _TILE_TYPE_LABELS[tile_type]
    return str(tile_type)


def _normalize_player_view(
    player_model: ApiPlayerViewModel | dict[str, object],
) -> ApiPlayerViewModel:
    if isinstance(player_model, ApiPlayerViewModel):
        return player_model
    return ApiPlayerViewModel.model_validate(player_model)


def _normalize_game_model(game: ApiGameModel | dict[str, object]) -> ApiGameModel:
    if isinstance(game, ApiGameModel):
        return game
    return ApiGameModel.model_validate(
        {
            "id": game.get("id"),
            "phase": game.get("phase", ""),
            "generation": game.get("generation", 0),
            "temperature": game.get("temperature", 0),
            "oxygenLevel": game.get("oxygenLevel", 0),
            "oceans": game.get("oceans", 0),
            "venusScaleLevel": game.get("venusScaleLevel", 0),
            "isTerraformed": game.get("isTerraformed", False),
            "gameAge": game.get("gameAge", 0),
            "undoCount": game.get("undoCount", 0),
            "passedPlayers": game.get("passedPlayers", []),
            "spaces": game.get("spaces", []),
            "milestones": game.get("milestones", []),
            "awards": game.get("awards", []),
        }
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
    player_model: ApiPlayerViewModel | dict[str, object],
) -> tuple[_PlayerSummary, list[_PlayerSummary]]:
    parsed_view = _normalize_player_view(player_model)
    this_player = parsed_view.thisPlayer
    player_color = player_model.get("color") if isinstance(player_model, dict) else None
    if not isinstance(player_color, str):
        player_color = this_player.color

    you: _PlayerSummary | None = None
    others: list[_PlayerSummary] = []
    for player in parsed_view.players:
        summary = _player_summary(player)
        if player.color == player_color:
            you = summary
        else:
            others.append(summary)

    return (you or _player_summary(this_player)), others


def _summarize_board(game: ApiGameModel | dict[str, object]) -> dict[str, object]:
    parsed_game = _normalize_game_model(game)
    spaces = parsed_game.spaces
    occupied = 0
    by_tile: dict[str, int] = {}
    for space in spaces:
        tile_type = space.tileType
        if tile_type is not None:
            occupied += 1
            key = _tile_type_name(tile_type)
            by_tile[key] = by_tile.get(key, 0) + 1
    return {
        "total_spaces": len(spaces),
        "occupied_spaces": occupied,
        "tile_counts": by_tile,
    }


def _summarize_milestones(game: ApiGameModel | dict[str, object]) -> list[dict[str, object]]:
    parsed_game = _normalize_game_model(game)
    summarized: list[dict[str, object]] = []
    for milestone in parsed_game.milestones:
        if not isinstance(milestone, ApiClaimedMilestoneModel):
            continue
        owner_color = milestone.color
        owner_name = milestone.playerName
        status = "claimed" if owner_color or owner_name else "available"

        scores: list[dict[str, object]] = []
        claimable_by: list[str] = []
        for score in milestone.scores or []:
            compact = {
                "color": score.color,
                "score": score.score,
                "claimable": score.claimable is True,
            }
            scores.append(compact)
            if score.claimable is True and isinstance(score.color, str):
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


def _summarize_awards(game: ApiGameModel | dict[str, object]) -> list[dict[str, object]]:
    parsed_game = _normalize_game_model(game)
    summarized: list[dict[str, object]] = []
    for award in parsed_game.awards:
        if not isinstance(award, ApiFundedAwardModel):
            continue
        funder_color = award.color
        funder_name = award.playerName
        status = "funded" if funder_color or funder_name else "unfunded"

        scores: list[dict[str, object]] = []
        for score in award.scores or []:
            scores.append(
                {
                    "color": score.color,
                    "score": score.score,
                }
            )

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
    game: ApiGameModel | dict[str, object],
    milestones: list[dict[str, object]],
    awards: list[dict[str, object]],
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
    parsed_game = _normalize_game_model(game)
    game_id = parsed_game.id or ""
    ma_key = f"{game_id}:{player_id}"
    prev = _LAST_MA_SNAPSHOT.get(ma_key)

    claimed_set = frozenset(m["name"] for m in milestones if m["status"] == "claimed")
    funded_set = frozenset(a["name"] for a in awards if a["status"] == "funded")
    claimable_set = frozenset(
        (m["name"], c) for m in milestones for c in m.get("claimable_by", [])
    )
    generation = parsed_game.generation
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
    game: ApiGameModel | dict[str, object], include_empty_spaces: bool = False
) -> dict[str, object]:
    parsed_game = _normalize_game_model(game)
    mars_spaces: list[dict[str, object]] = []
    for space in parsed_game.spaces:
        if not isinstance(space, ApiSpaceModel):
            continue
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
            space_data["tile_type"] = _tile_type_name(space.tileType)
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
        "game_id": parsed_game.id,
        "phase": parsed_game.phase,
        "generation": parsed_game.generation,
        "globals": {
            "temperature": parsed_game.temperature,
            "oxygen": parsed_game.oxygenLevel,
            "oceans": parsed_game.oceans,
            "venus": parsed_game.venusScaleLevel,
            "terraformed": parsed_game.isTerraformed,
        },
        "summary": _summarize_board(parsed_game),
        "spaces": mars_spaces,
    }


def _detect_new_opponent_cards(
    player_model: ApiPlayerViewModel | dict[str, object],
) -> list[dict[str, object]]:
    parsed_view = _normalize_player_view(player_model)
    game_id = parsed_view.game.id
    pid = parsed_view.id or ""
    if not isinstance(game_id, str) or not isinstance(pid, str):
        return []
    key = f"{game_id}:{pid}"

    this_color = parsed_view.thisPlayer.color
    players = parsed_view.players

    current: dict[str, Counter[str]] = {}
    for player in players:
        color = player.color
        if color == this_color:
            continue
        tableau = player.tableau or []
        names = [card.name for card in tableau if isinstance(card.name, str)]
        if isinstance(color, str):
            current[color] = Counter(names)

    previous = _LAST_OPPONENT_TABLEAU.get(key, {})
    events: list[dict[str, object]] = []
    for player in players:
        color = player.color
        if not isinstance(color, str) or color == this_color:
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
    player_model: ApiPlayerViewModel | dict[str, object],
    include_full_model: bool = False,
    include_board_state: bool = False,
    detail_level: str = DETAIL_LEVEL_FULL,
    base_url: str | None = None,
    player_id_fallback: str | None = None,
) -> dict[str, object]:
    parsed_player = _normalize_player_view(player_model)
    game = parsed_player.game
    normalized_detail_level = _normalize_detail_level(detail_level)
    waiting_for = _get_waiting_for_model(parsed_player)
    input_type = _input_type_name(waiting_for)
    you, opponents = _summarize_players(parsed_player)

    phase = game.phase
    show_board = include_board_state or (
        normalized_detail_level == DETAIL_LEVEL_FULL
        and phase in END_OF_GENERATION_PHASES
    )

    session: dict[str, object] = {
        "player_id": parsed_player.id or player_id_fallback or "",
    }
    if normalized_detail_level == DETAIL_LEVEL_FULL and base_url is not None:
        session["base_url"] = base_url

    game_state: dict[str, object] = {
        "id": game.id,
        "phase": game.phase,
        "generation": game.generation,
        "terraforming": {
            "temperature": game.temperature,
            "oxygen": game.oxygenLevel,
            "oceans": game.oceans,
            "venus": game.venusScaleLevel,
            "terraformed": game.isTerraformed,
        },
        "game_age": game.gameAge,
        "undo_count": game.undoCount,
        "passed_players": game.passedPlayers,
    }

    if normalized_detail_level == DETAIL_LEVEL_FULL:
        milestones = _summarize_milestones(game)
        awards = _summarize_awards(game)
        include_ma = _should_include_milestones_awards(
            game,
            milestones,
            awards,
            parsed_player.id,
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
        opponent_card_events = _detect_new_opponent_cards(parsed_player)
    else:
        opponents_state = [summary.to_minimal_payload() for summary in opponents]
        opponent_card_events = []

    result: dict[str, object] = {
        "session": session,
        "game": game_state,
        "you": you.to_full_payload(),
        "opponents": opponents_state,
        "waiting_for": _normalize_waiting_for(
            waiting_for, detail_level=normalized_detail_level
        ),
        "suggested_tools": _action_tools_for_input_type(input_type),
        "opponent_card_events": opponent_card_events,
    }

    if include_full_model:
        result["raw_player_model"] = parsed_player.model_dump(exclude_none=True)
    return result
