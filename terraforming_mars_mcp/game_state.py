from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Literal, NotRequired, TypedDict

from ._enums import (
    DetailLevel,
    InputType,
    ToolName,
    action_tools_for_input_type,
    strip_empty,
)
from .api_response_models import (
    GameModel as ApiGameModel,
    PlayerViewModel as ApiPlayerViewModel,
    PublicPlayerModel as ApiPublicPlayerModel,
    WaitingForInputModel as ApiWaitingForInputModel,
)
from .card_info import (
    card_info,
    compact_cards,
    extract_played_card_effects_and_actions,
)
from .waiting_for import (
    find_pass_option_index,
    input_type_name,
    normalize_waiting_for,
)

END_OF_GENERATION_PHASES = {"production", "solar", "intergeneration", "end"}


_FULL_STATE_INTERVAL = 10


@dataclass(frozen=True)
class _MilestonesAwardsSnapshot:
    generation: int
    claimed: frozenset[str]
    funded: frozenset[str]
    claimable: frozenset[tuple[str, str]]


@dataclass
class _SessionCache:
    """Per-(game, player) memory of what was already sent to the agent.

    Used to avoid re-sending unchanged data (constants, milestones, player
    summaries) on every auto-response.
    """

    opponent_tableau: dict[str, Counter[str]] = field(default_factory=dict)
    last_generation: int | None = None
    last_game_constants: dict[str, Any] | None = None
    # Responses since full player state was last included, keyed by detail level.
    responses_since_full_state: dict[str, int] = field(default_factory=dict)
    last_session: dict[str, Any] | None = None
    last_ma_snapshot: _MilestonesAwardsSnapshot | None = None


_SESSION_CACHES: dict[str, _SessionCache] = {}


def _session_cache(game_id: str, player_id: str) -> _SessionCache:
    return _SESSION_CACHES.setdefault(f"{game_id}:{player_id}", _SessionCache())


@dataclass(frozen=True)
class _ProductionSummary:
    mc: int
    steel: int
    titanium: int
    plants: int
    energy: int
    heat: int


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

    def to_full_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("active", None)
        if self.active:
            payload["active"] = True
        return payload

    def to_minimal_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "color": self.color,
            "tr": self.tr,
            "cards_in_hand_count": self.cards_in_hand_count,
        }
        if self.active:
            payload["active"] = True
        return payload


class _MilestoneScorePayload(TypedDict):
    color: str
    score: int
    claimable: NotRequired[bool]


class _MilestonePayload(TypedDict):
    name: str
    status: Literal["claimed", "available"]
    owner_color: NotRequired[str]
    owner_name: NotRequired[str]
    scores: NotRequired[list[_MilestoneScorePayload]]
    claimable_by: NotRequired[list[str]]


class _AwardScorePayload(TypedDict):
    color: str
    score: int


class _AwardPayload(TypedDict):
    name: str
    status: Literal["funded", "unfunded"]
    funder_color: NotRequired[str]
    funder_name: NotRequired[str]
    scores: NotRequired[list[_AwardScorePayload]]


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

_SPACE_BONUS_LABELS = (
    "titanium",
    "steel",
    "plant",
    "draw card",
    "heat",
    "ocean",
    "mega credits",
    "animal",
    "microbe",
    "energy",
    "data",
    "science",
    "energy production",
    "temperature",
    "restricted",
    "asteroid",
    "delegate",
    "colony",
    "temperature (4 MC)",
)


def _tile_type_label(tile_type: int) -> str:
    if 0 <= tile_type < len(_TILE_TYPE_LABELS):
        return _TILE_TYPE_LABELS[tile_type]
    return str(tile_type)


def _space_bonus_label(bonus: int) -> str:
    if 0 <= bonus < len(_SPACE_BONUS_LABELS):
        return _SPACE_BONUS_LABELS[bonus]
    return str(bonus)


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


def summarize_board(game: ApiGameModel) -> dict[str, Any]:
    spaces = game.spaces
    occupied = 0
    by_tile: dict[str, int] = {}
    for space in spaces:
        tile_type = space.tileType
        if tile_type is not None:
            occupied += 1
            key = _tile_type_label(tile_type)
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
            }
            if score.claimable is True:
                compact["claimable"] = True
                claimable_by.append(score.color)
            scores.append(compact)

        entry: _MilestonePayload = {"name": milestone.name, "status": status}
        if owner_color is not None:
            entry["owner_color"] = owner_color
        if owner_name is not None:
            entry["owner_name"] = owner_name
        if scores:
            entry["scores"] = scores
        if claimable_by:
            entry["claimable_by"] = claimable_by
        summarized.append(entry)
    return summarized


def _summarize_awards(game: ApiGameModel) -> list[_AwardPayload]:
    summarized: list[_AwardPayload] = []
    for award in game.awards:
        funder_color = award.color
        funder_name = award.playerName
        status: Literal["funded", "unfunded"] = (
            "funded" if funder_color or funder_name else "unfunded"
        )

        scores: list[_AwardScorePayload] = [
            {"color": s.color, "score": s.score} for s in (award.scores or [])
        ]

        award_entry: _AwardPayload = {"name": award.name, "status": status}
        if funder_color is not None:
            award_entry["funder_color"] = funder_color
        if funder_name is not None:
            award_entry["funder_name"] = funder_name
        if scores:
            award_entry["scores"] = scores
        summarized.append(award_entry)
    return summarized


def _should_include_milestones_awards(
    milestones: list[_MilestonePayload],
    awards: list[_AwardPayload],
    generation: int,
    cache: _SessionCache,
) -> bool:
    """Include milestones/awards once per generation or when a critical change occurs.

    Critical changes:
    - A milestone was newly claimed (status changed to 'claimed')
    - An award was newly funded (status changed to 'funded')
    - A player became newly claimable for a milestone
    - Generation changed (show once at start of each generation)
    - First call for this game (no previous snapshot)
    """
    current = _MilestonesAwardsSnapshot(
        generation=generation,
        claimed=frozenset(m["name"] for m in milestones if m["status"] == "claimed"),
        funded=frozenset(a["name"] for a in awards if a["status"] == "funded"),
        claimable=frozenset(
            (m["name"], c) for m in milestones for c in m.get("claimable_by", [])
        ),
    )
    include = cache.last_ma_snapshot != current
    cache.last_ma_snapshot = current
    return include


def full_board_state(
    game: ApiGameModel, include_empty_spaces: bool = False
) -> dict[str, Any]:
    mars_spaces: list[dict[str, Any]] = []
    for space in game.spaces:
        if not include_empty_spaces and space.tileType is None:
            continue
        space_data: dict[str, Any] = strip_empty(
            {
                "id": space.id,
                "x": space.x,
                "y": space.y,
                "space_type": space.spaceType,
                "bonus": [_space_bonus_label(b) for b in space.bonus]
                if space.bonus
                else None,
                "tile_type": _tile_type_label(space.tileType)
                if space.tileType is not None
                else None,
                "owner_color": space.color,
                "co_owner_color": space.coOwner,
                "highlight": space.highlight,
                "gagarin": space.gagarin,
                "rotated": space.rotated,
                "cathedral": space.cathedral,
                "nomads": space.nomads,
                "underground_resource": space.undergroundResource,
                "excavator": space.excavator,
            }
        )
        mars_spaces.append(space_data)

    return {
        "game_id": game.id,
        "phase": game.phase,
        "generation": game.generation,
        "reminder": "Read agent-prompts/no_guide/tharsis-board-shape.md for full board guide",
        "globals": {
            "temperature": game.temperature,
            "oxygen": game.oxygenLevel,
            "oceans": game.oceans,
            "venus": game.venusScaleLevel,
            "terraformed": game.isTerraformed,
        },
        "summary": summarize_board(game),
        "spaces": mars_spaces,
    }


def _new_opponent_cards_from_counts(
    player_model: ApiPlayerViewModel,
    previous: dict[str, Counter[str]],
) -> tuple[list[dict[str, Any]], dict[str, Counter[str]]]:
    this_color = player_model.thisPlayer.color
    current: dict[str, Counter[str]] = {}
    for player in player_model.players:
        color = player.color
        if color == this_color:
            continue
        tableau = player.tableau or []
        current[color] = Counter(card.name for card in tableau)
    events: list[dict[str, Any]] = []
    for player in player_model.players:
        color = player.color
        if color == this_color:
            continue
        old_counts = previous.get(color, Counter())
        new_counts = current.get(color, Counter())
        delta = new_counts - old_counts
        for card_name, count in delta.items():
            for _ in range(count):
                info = card_info(card_name, include_play_details=True)
                event: dict[str, Any] = {
                    "player_name": player.name,
                    "player_color": color,
                    "card_name": card_name,
                    "tags": info.get("tags", []),
                    "ongoing_effects": info.get("ongoing_effects", []),
                    "activated_actions": info.get("activated_actions", []),
                    "play_requirements_text": info.get("play_requirements_text"),
                    "on_play_effect_text": info.get("on_play_effect_text"),
                    "cost": info.get("base_cost"),
                    "vp": info.get("vp"),
                }
                events.append(event)
    return events, current


def _detect_new_opponent_cards(
    player_model: ApiPlayerViewModel,
    cache: _SessionCache,
) -> list[dict[str, Any]]:
    events, current = _new_opponent_cards_from_counts(
        player_model, cache.opponent_tableau
    )
    cache.opponent_tableau = current
    return events


# Expansion keys that map to groups of fields to strip when disabled.
_EXPANSION_FIELD_GROUPS: dict[str, dict[str, list[str]]] = {
    "venus": {
        "player": ["venusScaleLevel"],
        "globalParameterSteps": ["venus"],
    },
    "moon": {
        "player": [],
        "globalParameterSteps": [
            "moon-habitat",
            "moon-mining",
            "moon-logistics",
        ],
        "victoryPointsBreakdown": [
            "moonHabitats",
            "moonMines",
            "moonRoads",
        ],
    },
    "colonies": {
        "player": ["coloniesCount", "fleetSize", "tradesThisGeneration"],
    },
    "turmoil": {
        "player": ["influence"],
    },
    "underworld": {
        "player": ["underworldData"],
    },
    "pathfinders": {
        "victoryPointsBreakdown": ["planetaryTracks"],
    },
}


def _strip_expansion_fields(
    player_data: dict[str, Any],
    disabled_expansions: set[str],
) -> None:
    """Remove fields from a player dict that belong to disabled expansions."""
    for expansion in disabled_expansions:
        groups = _EXPANSION_FIELD_GROUPS.get(expansion)
        if groups is None:
            continue
        for key in groups.get("player", []):
            player_data.pop(key, None)

        gps = player_data.get("globalParameterSteps")
        if isinstance(gps, dict):
            for key in groups.get("globalParameterSteps", []):
                gps.pop(key, None)

        vpb = player_data.get("victoryPointsBreakdown")
        if isinstance(vpb, dict):
            for key in groups.get("victoryPointsBreakdown", []):
                vpb.pop(key, None)


def thin_raw_player_model(raw: dict[str, Any]) -> dict[str, Any]:
    """Apply all thinning passes to a raw ``model_dump`` of the player model."""

    # Drop `thisPlayer` — it duplicates one entry in `players`.
    raw.pop("thisPlayer", None)

    # Determine disabled expansions from gameOptions.
    game = raw.get("game")
    disabled_expansions: set[str] = set()
    phase: str = ""
    if isinstance(game, dict):
        phase = game.get("phase", "")
        game_options = game.get("gameOptions")
        if isinstance(game_options, dict):
            expansions = game_options.get("expansions")
            if isinstance(expansions, dict):
                for exp_name, enabled in expansions.items():
                    if not enabled:
                        disabled_expansions.add(exp_name)

    # Strip disabled-expansion fields from game-level globals.
    if isinstance(game, dict):
        # Strip venus scale from game when venus is disabled.
        if "venus" in disabled_expansions:
            game.pop("venusScaleLevel", None)
        # Strip globalsPerGeneration venus entries.
        gpg = game.get("globalsPerGeneration")
        if isinstance(gpg, list) and "venus" in disabled_expansions:
            for entry in gpg:
                if isinstance(entry, dict):
                    entry.pop("venus", None)

    # Process each player.
    players = raw.get("players")
    if isinstance(players, list):
        for player_data in players:
            if not isinstance(player_data, dict):
                continue

            # Filter resources: 0 from tableau cards.
            tableau = player_data.get("tableau")
            if isinstance(tableau, list):
                for card in tableau:
                    if card.get("resources") == 0:
                        card.pop("resources", None)

            # Strip disabled-expansion fields from player data.
            _strip_expansion_fields(player_data, disabled_expansions)

            # Gate dealtX cards on phase == "end".
            if phase != "end":
                player_data.pop("dealtCorporationCards", None)
                player_data.pop("dealtPreludeCards", None)
                player_data.pop("dealtProjectCards", None)
                player_data.pop("dealtCeoCards", None)

            # Gate VP breakdown details on phase == "end".
            vpb = player_data.get("victoryPointsBreakdown")
            if isinstance(vpb, dict) and phase != "end":
                vpb.pop("detailsCards", None)
                vpb.pop("detailsMilestones", None)
                vpb.pop("detailsAwards", None)
                vpb.pop("detailsPlanetaryTracks", None)

            # Strip empty selfReplicatingRobotsCards and all-off
            # protectedResources/protectedProduction.
            if player_data.get("selfReplicatingRobotsCards") == []:
                player_data.pop("selfReplicatingRobotsCards", None)
            pr = player_data.get("protectedResources")
            if isinstance(pr, dict) and all(v == "off" for v in pr.values()):
                player_data.pop("protectedResources", None)
            pp = player_data.get("protectedProduction")
            if isinstance(pp, dict) and all(v == "off" for v in pp.values()):
                player_data.pop("protectedProduction", None)

            # Strip victoryPointsByGeneration mid-game.
            if phase != "end":
                player_data.pop("victoryPointsByGeneration", None)

            # Strip zero-valued tags.
            tags = player_data.get("tags")
            if isinstance(tags, dict):
                player_data["tags"] = {k: v for k, v in tags.items() if v}

    # Also strip dealtX and VP details from the top-level model (outside players).
    if phase != "end":
        raw.pop("dealtCorporationCards", None)
        raw.pop("dealtPreludeCards", None)
        raw.pop("dealtProjectCards", None)
        raw.pop("dealtCeoCards", None)

    return raw


def _build_game_constants(game: ApiGameModel) -> dict[str, Any]:
    """Core game constants that rarely change mid-turn."""
    terraforming: dict[str, Any] = {
        "temperature": game.temperature,
        "oxygen": game.oxygenLevel,
        "oceans": game.oceans,
    }
    if game.isTerraformed:
        terraforming["terraformed"] = True
    game_extra = game.model_extra or {}
    game_options_raw = game_extra.get("gameOptions")
    if isinstance(game_options_raw, dict):
        expansions = game_options_raw.get("expansions")
        if isinstance(expansions, dict) and expansions.get("venus"):
            terraforming["venus"] = game.venusScaleLevel
    return {
        "phase": game.phase,
        "generation": game.generation,
        "terraforming": terraforming,
    }


def _build_game_state_section(
    game: ApiGameModel,
    cache: _SessionCache,
    detail_level: DetailLevel,
    show_board: bool,
) -> tuple[dict[str, Any], bool]:
    """Build the `game` payload; returns it plus whether a new generation started."""
    generation = game.generation
    game_constants = _build_game_constants(game)

    # Send full constants on first call, generation change, or value change.
    is_gen_start = cache.last_generation != generation
    constants_changed = is_gen_start or cache.last_game_constants != game_constants
    cache.last_generation = generation
    cache.last_game_constants = game_constants

    game_state: dict[str, Any] = {
        "game_age": game.gameAge,
    }
    if game.id:
        game_state["id"] = game.id
    if game.undoCount:
        game_state["undo_count"] = game.undoCount
    if game.passedPlayers:
        game_state["passed_players"] = game.passedPlayers

    if constants_changed:
        game_state.update(game_constants)
    else:
        # Only include generation (always useful context) when constants unchanged.
        game_state["generation"] = generation

    if detail_level == DetailLevel.FULL:
        milestones = _summarize_milestones(game)
        awards = _summarize_awards(game)
        if _should_include_milestones_awards(milestones, awards, generation, cache):
            game_state["milestones"] = milestones
            game_state["awards"] = awards
        else:
            game_state["milestones_changed"] = False
    if show_board:
        game_state["board"] = summarize_board(game)
        game_state["board_visible"] = True

    return game_state, is_gen_start


def _should_include_player_state(
    cache: _SessionCache, detail_level: DetailLevel, is_gen_start: bool
) -> bool:
    """Include you/opponents at generation start or every N responses."""
    key = str(detail_level)
    responses_since = cache.responses_since_full_state.get(key, _FULL_STATE_INTERVAL)
    include = is_gen_start or responses_since >= _FULL_STATE_INTERVAL
    cache.responses_since_full_state[key] = 0 if include else responses_since + 1
    return include


def _build_generation_start(
    player_model: ApiPlayerViewModel, generation: int
) -> dict[str, Any]:
    gen_start_cards = compact_cards(
        player_model.cardsInHand,
        detail_level=DetailLevel.FULL,
        generation=generation,
        auto_response=False,
    )
    return {
        "cards_in_hand_count": len(gen_start_cards),
        "cards_in_hand": gen_start_cards,
        "played_card_effects_and_actions": extract_played_card_effects_and_actions(
            player_model.thisPlayer
        ),
    }


def _suggested_tools(
    input_type: str | None, waiting_for: ApiWaitingForInputModel | None
) -> list[str]:
    suggested = action_tools_for_input_type(input_type)
    if input_type == InputType.OR_OPTIONS.value:
        suggested.append(ToolName.SUBMIT_MULTI_ACTIONS.value)
        if waiting_for is not None and find_pass_option_index(waiting_for) is not None:
            suggested.append(ToolName.PASS_TURN.value)
    return suggested


def build_agent_state(
    player_model: ApiPlayerViewModel,
    include_full_model: bool = False,
    include_board_state: bool = False,
    detail_level: DetailLevel = DetailLevel.FULL,
    base_url: str | None = None,
    player_id_fallback: str | None = None,
    auto_response: bool = False,
    between_turns_actions: list[str] | None = None,
) -> dict[str, Any]:
    game = player_model.game
    waiting_for = player_model.waitingFor
    input_type = input_type_name(waiting_for)
    you, opponents = _summarize_players(player_model)

    show_board = include_board_state or (
        detail_level == DetailLevel.FULL and game.phase in END_OF_GENERATION_PHASES
    )

    generation = game.generation
    player_id = player_model.id or player_id_fallback or ""
    cache = _session_cache(game.id or "", player_id)

    session: dict[str, Any] = {"player_id": player_id}
    if detail_level == DetailLevel.FULL and base_url is not None:
        session["base_url"] = base_url

    game_state, is_gen_start = _build_game_state_section(
        game, cache, detail_level, show_board
    )

    if detail_level == DetailLevel.FULL:
        you_state = you.to_full_payload()
        opponents_state = [summary.to_full_payload() for summary in opponents]
        opponent_new_cards = _detect_new_opponent_cards(player_model, cache)
    else:
        you_state = you.to_minimal_payload()
        opponents_state = [summary.to_minimal_payload() for summary in opponents]
        opponent_new_cards = []

    result: dict[str, Any] = {}
    if cache.last_session != session:
        cache.last_session = session
        result["session"] = session
    result["game"] = game_state
    if _should_include_player_state(cache, detail_level, is_gen_start):
        result["you"] = you_state
        result["opponents"] = opponents_state
    result["waiting_for"] = normalize_waiting_for(
        waiting_for,
        detail_level=detail_level,
        generation=generation,
        auto_response=auto_response,
    )
    if auto_response and detail_level == DetailLevel.FULL and is_gen_start:
        result["generation_start"] = _build_generation_start(player_model, generation)
    result["suggested_tools"] = _suggested_tools(input_type, waiting_for)
    result["opponent_new_cards"] = opponent_new_cards
    if between_turns_actions:
        result["opponent_actions_between_turns"] = between_turns_actions

    if include_full_model:
        result["raw_player_model"] = thin_raw_player_model(
            player_model.model_dump(exclude_none=True)
        )
    return strip_empty(result)
