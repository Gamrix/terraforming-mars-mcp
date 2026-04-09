from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Literal, NotRequired, TypedDict

from .api_response_models import (
    GameModel as ApiGameModel,
    PlayerViewModel as ApiPlayerViewModel,
    PublicPlayerModel as ApiPublicPlayerModel,
)
from ._enums import DetailLevel, InputType, ToolName, _action_tools_for_input_type
from .card_info import (
    _card_info,
    _compact_cards,
    _extract_played_card_effects_and_actions,
    _normalize_detail_level,
)
from .waiting_for import (
    _find_pass_option_index,
    _input_type_name,
    _normalize_waiting_for,
)

END_OF_GENERATION_PHASES = {"production", "solar", "intergeneration", "end"}


def _strip_empty(obj: Any) -> Any:
    """Recursively strip None values and empty lists from dicts.

    Leaves other falsy values (0, False, empty strings) untouched since they
    carry semantic meaning in game state payloads.
    """
    if isinstance(obj, dict):
        return {k: _strip_empty(v) for k, v in obj.items() if v is not None and v != []}
    if isinstance(obj, list):
        return [_strip_empty(item) for item in obj]
    return obj


_LAST_OPPONENT_TABLEAU: dict[str, dict[str, Counter[str]]] = {}
# Tracks (generation, constants_dict) so we send full constants once per gen.
_LAST_GAME_CONSTANTS: dict[str, tuple[int, dict[str, Any]]] = {}
# Counts responses since the last time full player/game state was included.
_RESPONSES_SINCE_FULL_STATE: dict[str, int] = {}
_FULL_STATE_INTERVAL = 10


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
        return asdict(self)


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
        payload: dict[str, Any] = {
            "name": self.name,
            "color": self.color,
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


_LAST_MA_SNAPSHOT: dict[str, _MilestonesAwardsSnapshot] = {}


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


def _generation_start_context(player_model: ApiPlayerViewModel) -> dict[str, Any]:
    cards_in_hand = _compact_cards(
        player_model.cardsInHand,
        detail_level=DetailLevel.FULL,
        generation=player_model.game.generation,
        auto_response=False,
    )
    return {
        "cards_in_hand_count": len(cards_in_hand),
        "cards_in_hand": cards_in_hand,
        "played_card_effects_and_actions": _extract_played_card_effects_and_actions(
            player_model.thisPlayer
        ),
    }


def _summarize_board(game: ApiGameModel) -> dict[str, Any]:
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
) -> dict[str, Any]:
    mars_spaces: list[dict[str, Any]] = []
    for space in game.spaces:
        if not include_empty_spaces and space.tileType is None:
            continue
        space_data: dict[str, Any] = {
            "id": space.id,
            "x": space.x,
            "y": space.y,
            "space_type": space.spaceType,
        }
        if space.bonus:
            space_data["bonus"] = [_space_bonus_label(bonus) for bonus in space.bonus]
        if space.tileType is not None:
            space_data["tile_type"] = _tile_type_label(space.tileType)
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
        "reminder": "Read agent-prompts/no_guide/tharsis-board-shape.md for full board guide",
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


def _opponent_tableau_counts(
    player_model: ApiPlayerViewModel,
) -> dict[str, Counter[str]]:
    this_color = player_model.thisPlayer.color
    current: dict[str, Counter[str]] = {}
    for player in player_model.players:
        color = player.color
        if color == this_color:
            continue
        tableau = player.tableau or []
        names = [card.name for card in tableau]
        current[color] = Counter(names)
    return current


def _new_opponent_cards_from_counts(
    player_model: ApiPlayerViewModel,
    previous: dict[str, Counter[str]],
) -> tuple[list[dict[str, Any]], dict[str, Counter[str]]]:
    this_color = player_model.thisPlayer.color
    current = _opponent_tableau_counts(player_model)
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
                info = _card_info(card_name, include_play_details=True)
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
                    "discounted_cost": info.get("base_cost"),
                }
                vp = info.get("vp")
                if vp is not None:
                    event["vp"] = vp
                events.append(event)
    return events, current


def _detect_new_opponent_cards(
    player_model: ApiPlayerViewModel,
) -> list[dict[str, Any]]:
    game_id = player_model.game.id
    pid = player_model.id or ""
    if not isinstance(game_id, str) or not isinstance(pid, str):
        return []
    key = f"{game_id}:{pid}"

    previous = _LAST_OPPONENT_TABLEAU.get(key, {})
    events, current = _new_opponent_cards_from_counts(player_model, previous)
    _LAST_OPPONENT_TABLEAU[key] = current
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


def _strip_zero_resources_from_tableau(
    tableau: list[dict[str, Any]],
) -> None:
    """Remove ``resources: 0`` entries from tableau card dicts."""
    for card in tableau:
        if card.get("resources") == 0:
            card.pop("resources", None)


def _thin_raw_player_model(
    raw: dict[str, Any],
    this_color: str,
) -> dict[str, Any]:
    """Apply all thinning passes to a raw ``model_dump`` of the player model."""

    # 1. Drop `thisPlayer` — it duplicates one entry in `players`.
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

    # 3. Strip disabled-expansion fields from game-level globals.
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

            # 2. Filter resources: 0 from tableau cards.
            tableau = player_data.get("tableau")
            if isinstance(tableau, list):
                _strip_zero_resources_from_tableau(tableau)

            # 3. Strip disabled-expansion fields from player data.
            _strip_expansion_fields(player_data, disabled_expansions)

            # 4. Gate dealtX cards on phase == "end".
            if phase != "end":
                player_data.pop("dealtCorporationCards", None)
                player_data.pop("dealtPreludeCards", None)
                player_data.pop("dealtProjectCards", None)
                player_data.pop("dealtCeoCards", None)

            # 5. Gate VP breakdown details on phase == "end".
            vpb = player_data.get("victoryPointsBreakdown")
            if isinstance(vpb, dict) and phase != "end":
                vpb.pop("detailsCards", None)
                vpb.pop("detailsMilestones", None)
                vpb.pop("detailsAwards", None)
                vpb.pop("detailsPlanetaryTracks", None)

            # 9. Strip empty selfReplicatingRobotsCards and all-off
            #    protectedResources/protectedProduction.
            if player_data.get("selfReplicatingRobotsCards") == []:
                player_data.pop("selfReplicatingRobotsCards", None)
            pr = player_data.get("protectedResources")
            if isinstance(pr, dict) and all(v == "off" for v in pr.values()):
                player_data.pop("protectedResources", None)
            pp = player_data.get("protectedProduction")
            if isinstance(pp, dict) and all(v == "off" for v in pp.values()):
                player_data.pop("protectedProduction", None)

            # 10. Strip victoryPointsByGeneration mid-game.
            if phase != "end":
                player_data.pop("victoryPointsByGeneration", None)

            # 11. Strip zero-valued tags.
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


def _build_agent_state(
    player_model: ApiPlayerViewModel,
    include_full_model: bool = False,
    include_board_state: bool = False,
    detail_level: str | DetailLevel = DetailLevel.FULL,
    base_url: str | None = None,
    player_id_fallback: str | None = None,
    auto_response: bool = False,
    between_turns_actions: list[str] | None = None,
) -> dict[str, Any]:
    game = player_model.game
    normalized_detail_level = _normalize_detail_level(detail_level)
    waiting_for = player_model.waitingFor
    input_type = _input_type_name(waiting_for)
    you, opponents = _summarize_players(player_model)

    phase = game.phase
    show_board = include_board_state or (
        normalized_detail_level == DetailLevel.FULL
        and phase in END_OF_GENERATION_PHASES
    )

    generation = game.generation
    player_id = player_model.id or player_id_fallback or ""
    game_id = game.id or ""
    constants_key = f"{game_id}:{player_id}"

    # Build session and game constants, then check if they changed.
    session: dict[str, Any] = {
        "player_id": player_id,
    }
    if normalized_detail_level == DetailLevel.FULL and base_url is not None:
        session["base_url"] = base_url

    # Core game constants that rarely change mid-turn.
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
    game_constants: dict[str, Any] = {
        "phase": game.phase,
        "generation": generation,
        "terraforming": terraforming,
    }

    prev = _LAST_GAME_CONSTANTS.get(constants_key)
    prev_gen, prev_constants = prev if prev is not None else (None, None)
    # Send full constants on first call, generation change, or value change.
    constants_changed = prev_gen != generation or prev_constants != game_constants
    _LAST_GAME_CONSTANTS[constants_key] = (generation, game_constants)

    game_state: dict[str, Any] = {
        "game_age": game.gameAge,
    }
    if game_id:
        game_state["id"] = game_id
    if game.undoCount:
        game_state["undo_count"] = game.undoCount
    if game.passedPlayers:
        game_state["passed_players"] = game.passedPlayers

    if constants_changed:
        game_state.update(game_constants)
    else:
        # Only include generation (always useful context) when constants unchanged.
        game_state["generation"] = generation

    if normalized_detail_level == DetailLevel.FULL:
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

    if normalized_detail_level == DetailLevel.FULL:
        opponents_state = [summary.to_full_payload() for summary in opponents]
        opponent_new_cards = _detect_new_opponent_cards(player_model)
    else:
        opponents_state = [summary.to_minimal_payload() for summary in opponents]
        opponent_new_cards = []

    you_state = (
        you.to_full_payload()
        if normalized_detail_level == DetailLevel.FULL
        else you.to_minimal_payload()
    )

    # Include you/opponents at generation start or every N responses.
    is_gen_start = prev_gen != generation
    state_counter_key = f"{constants_key}:{normalized_detail_level}"
    responses_since = _RESPONSES_SINCE_FULL_STATE.get(
        state_counter_key, _FULL_STATE_INTERVAL
    )
    include_player_state = is_gen_start or responses_since >= _FULL_STATE_INTERVAL
    if include_player_state:
        _RESPONSES_SINCE_FULL_STATE[state_counter_key] = 0
    else:
        _RESPONSES_SINCE_FULL_STATE[state_counter_key] = responses_since + 1

    result: dict[str, Any] = {}
    if constants_changed:
        result["session"] = session
    result["game"] = game_state
    if include_player_state:
        result["you"] = you_state
        result["opponents"] = opponents_state
    result["waiting_for"] = _normalize_waiting_for(
        waiting_for,
        detail_level=normalized_detail_level,
        generation=generation,
        auto_response=auto_response,
    )
    if (
        auto_response
        and normalized_detail_level == DetailLevel.FULL
        and prev_gen != generation
    ):
        result["generation_start"] = _generation_start_context(player_model)
    suggested_tools = _action_tools_for_input_type(input_type)
    if (
        input_type == InputType.OR_OPTIONS.value
        and waiting_for is not None
        and _find_pass_option_index(waiting_for) is not None
    ):
        suggested_tools.append(ToolName.PASS_TURN.value)
    result["suggested_tools"] = suggested_tools
    result["opponent_new_cards"] = opponent_new_cards
    if between_turns_actions:
        result["opponent_actions_between_turns"] = between_turns_actions

    if include_full_model:
        result["raw_player_model"] = _thin_raw_player_model(
            player_model.model_dump(exclude_none=True),
            this_color=player_model.thisPlayer.color,
        )
    return _strip_empty(result)
