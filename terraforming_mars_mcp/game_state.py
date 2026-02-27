from __future__ import annotations

from collections import Counter
from typing import Any

try:
    from .api_response_models import (
        ClaimedMilestoneModel as ApiClaimedMilestoneModel,
        FundedAwardModel as ApiFundedAwardModel,
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
except ImportError:
    from api_response_models import (  # type: ignore[no-redef]
        ClaimedMilestoneModel as ApiClaimedMilestoneModel,
        FundedAwardModel as ApiFundedAwardModel,
        PlayerViewModel as ApiPlayerViewModel,
        PublicPlayerModel as ApiPublicPlayerModel,
        SpaceModel as ApiSpaceModel,
    )
    from _enums import _action_tools_for_input_type  # type: ignore[no-redef]
    from card_info import (
        DETAIL_LEVEL_FULL,
        _card_info,
        _normalize_detail_level,
    )  # type: ignore[no-redef]
    from waiting_for import (
        _get_waiting_for_model,
        _input_type_name,
        _normalize_waiting_for,
    )  # type: ignore[no-redef]

END_OF_GENERATION_PHASES = {"production", "solar", "intergeneration", "end"}

_LAST_OPPONENT_TABLEAU: dict[str, dict[str, Counter[str]]] = {}
_LAST_MA_SNAPSHOT: dict[str, dict[str, Any]] = {}


def _summarize_players(
    player_model: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    parsed_view = ApiPlayerViewModel.model_validate(player_model)
    this_player = parsed_view.thisPlayer
    player_color = player_model.get("color")
    if not isinstance(player_color, str) and isinstance(
        this_player, ApiPublicPlayerModel
    ):
        this_color = this_player.color
        if isinstance(this_color, str):
            player_color = this_color

    you: dict[str, Any] = {}
    others: list[dict[str, Any]] = []
    all_players = parsed_view.players or []
    for p in all_players:
        if not isinstance(p, ApiPublicPlayerModel):
            continue
        compact = {
            "name": p.name,
            "color": p.color,
            "active": p.isActive,
            "tr": p.terraformRating,
            "mc": p.megaCredits,
            "steel": p.steel,
            "titanium": p.titanium,
            "plants": p.plants,
            "energy": p.energy,
            "heat": p.heat,
            "prod": {
                "mc": p.megaCreditProduction,
                "steel": p.steelProduction,
                "titanium": p.titaniumProduction,
                "plants": p.plantProduction,
                "energy": p.energyProduction,
                "heat": p.heatProduction,
            },
            "cards_in_hand_count": p.cardsInHandNbr,
            "actions_this_generation": p.actionsThisGeneration,
        }
        if p.color == player_color:
            you = compact
        else:
            others.append(compact)

    if not you and isinstance(this_player, ApiPublicPlayerModel):
        you = {
            "name": this_player.name,
            "color": this_player.color,
            "active": this_player.isActive,
            "tr": this_player.terraformRating,
            "mc": this_player.megaCredits,
            "steel": this_player.steel,
            "titanium": this_player.titanium,
            "plants": this_player.plants,
            "energy": this_player.energy,
            "heat": this_player.heat,
            "prod": {
                "mc": this_player.megaCreditProduction,
                "steel": this_player.steelProduction,
                "titanium": this_player.titaniumProduction,
                "plants": this_player.plantProduction,
                "energy": this_player.energyProduction,
                "heat": this_player.heatProduction,
            },
            "cards_in_hand_count": this_player.cardsInHandNbr,
            "actions_this_generation": this_player.actionsThisGeneration,
        }
    return you, others


def _summarize_board(game: dict[str, Any]) -> dict[str, Any]:
    parsed_game = game if isinstance(game, dict) else {}
    spaces_raw = parsed_game.get("spaces")
    spaces = (
        [ApiSpaceModel.model_validate(space) for space in spaces_raw]
        if isinstance(spaces_raw, list)
        else []
    )
    occupied = 0
    by_tile: dict[str, int] = {}
    for space in spaces:
        tile_type = space.tileType
        if tile_type is not None:
            occupied += 1
            key = str(tile_type)
            by_tile[key] = by_tile.get(key, 0) + 1
    return {
        "total_spaces": len(spaces)
        if spaces
        else (len(spaces_raw) if isinstance(spaces_raw, list) else None),
        "occupied_spaces": occupied,
        "tile_counts": by_tile,
    }


def _summarize_milestones(game: dict[str, Any]) -> list[dict[str, Any]]:
    milestones_raw = game.get("milestones")
    if not isinstance(milestones_raw, list):
        return []

    summarized: list[dict[str, Any]] = []
    for raw_milestone in milestones_raw:
        milestone = ApiClaimedMilestoneModel.model_validate(raw_milestone)
        owner_color = milestone.color
        owner_name = milestone.playerName
        status = "claimed" if owner_color or owner_name else "available"

        scores: list[dict[str, Any]] = []
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


def _summarize_awards(game: dict[str, Any]) -> list[dict[str, Any]]:
    awards_raw = game.get("awards")
    if not isinstance(awards_raw, list):
        return []

    summarized: list[dict[str, Any]] = []
    for raw_award in awards_raw:
        award = ApiFundedAwardModel.model_validate(raw_award)
        funder_color = award.color
        funder_name = award.playerName
        status = "funded" if funder_color or funder_name else "unfunded"

        scores: list[dict[str, Any]] = []
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
    game: dict[str, Any],
    milestones: list[dict[str, Any]],
    awards: list[dict[str, Any]],
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
    game_id = game.get("id", "")
    ma_key = f"{game_id}:{player_id}"
    prev = _LAST_MA_SNAPSHOT.get(ma_key)

    claimed_set = frozenset(m["name"] for m in milestones if m["status"] == "claimed")
    funded_set = frozenset(a["name"] for a in awards if a["status"] == "funded")
    claimable_set = frozenset(
        (m["name"], c) for m in milestones for c in m.get("claimable_by", [])
    )
    generation = game.get("generation")

    current = {
        "generation": generation,
        "claimed": claimed_set,
        "funded": funded_set,
        "claimable": claimable_set,
    }

    include = False
    if prev is None:
        include = True
    elif prev["generation"] != generation:
        include = True
    elif prev["claimed"] != claimed_set:
        include = True
    elif prev["funded"] != funded_set:
        include = True
    elif prev["claimable"] != claimable_set:
        include = True

    _LAST_MA_SNAPSHOT[ma_key] = current
    return include


def _full_board_state(
    game: dict[str, Any], include_empty_spaces: bool = False
) -> dict[str, Any]:
    spaces = game.get("spaces")
    mars_spaces: list[dict[str, Any]] = []
    if isinstance(spaces, list):
        for raw_space in spaces:
            if not isinstance(raw_space, dict):
                continue
            space = ApiSpaceModel.model_validate(raw_space)
            if not include_empty_spaces and space.tileType is None:
                continue
            space_data: dict[str, Any] = {
                "id": space.id,
                "x": space.x,
                "y": space.y,
                "space_type": space.spaceType,
            }
            if space.bonus:
                space_data["bonus"] = space.bonus
            if space.tileType is not None:
                space_data["tile_type"] = space.tileType
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
        "game_id": game.get("id"),
        "phase": game.get("phase"),
        "generation": game.get("generation"),
        "globals": {
            "temperature": game.get("temperature"),
            "oxygen": game.get("oxygenLevel"),
            "oceans": game.get("oceans"),
            "venus": game.get("venusScaleLevel"),
            "terraformed": game.get("isTerraformed"),
        },
        "summary": _summarize_board(game),
        "spaces": mars_spaces,
    }


def _detect_new_opponent_cards(player_model: dict[str, Any]) -> list[dict[str, Any]]:
    parsed_view = ApiPlayerViewModel.model_validate(player_model)
    if parsed_view.game is None:
        return []
    game_id = parsed_view.game.id
    pid = parsed_view.id or ""
    if not isinstance(game_id, str) or not isinstance(pid, str):
        return []
    key = f"{game_id}:{pid}"

    this_color = (
        parsed_view.thisPlayer.color
        if isinstance(parsed_view.thisPlayer, ApiPublicPlayerModel)
        else None
    )
    players = parsed_view.players or []

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
    events: list[dict[str, Any]] = []
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
                event: dict[str, Any] = {
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
    player_model: dict[str, Any],
    include_full_model: bool = False,
    include_board_state: bool = False,
    detail_level: str = DETAIL_LEVEL_FULL,
    base_url: str | None = None,
    player_id_fallback: str | None = None,
) -> dict[str, Any]:
    normalized_detail_level = _normalize_detail_level(detail_level)
    game = (
        player_model.get("game", {})
        if isinstance(player_model.get("game"), dict)
        else {}
    )
    waiting_for = _get_waiting_for_model(player_model)
    input_type = _input_type_name(waiting_for)
    you, opponents = _summarize_players(player_model)

    phase = game.get("phase")
    show_board = include_board_state or (
        normalized_detail_level == DETAIL_LEVEL_FULL
        and isinstance(phase, str)
        and phase in END_OF_GENERATION_PHASES
    )

    session: dict[str, Any] = {
        "player_id": player_model.get("id", player_id_fallback or ""),
    }
    if normalized_detail_level == DETAIL_LEVEL_FULL and base_url is not None:
        session["base_url"] = base_url

    game_state: dict[str, Any] = {
        "id": game.get("id"),
        "phase": game.get("phase"),
        "generation": game.get("generation"),
        "terraforming": {
            "temperature": game.get("temperature"),
            "oxygen": game.get("oxygenLevel"),
            "oceans": game.get("oceans"),
            "venus": game.get("venusScaleLevel"),
            "terraformed": game.get("isTerraformed"),
        },
        "game_age": game.get("gameAge"),
        "undo_count": game.get("undoCount"),
        "passed_players": game.get("passedPlayers"),
    }

    if normalized_detail_level == DETAIL_LEVEL_FULL:
        milestones = _summarize_milestones(game)
        awards = _summarize_awards(game)
        include_ma = _should_include_milestones_awards(
            game,
            milestones,
            awards,
            player_model.get("id", ""),
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
        opponents_state = opponents
        opponent_card_events = _detect_new_opponent_cards(player_model)
    else:
        opponents_state = [
            {
                "name": p.get("name"),
                "color": p.get("color"),
                "active": p.get("active"),
                "tr": p.get("tr"),
                "cards_in_hand_count": p.get("cards_in_hand_count"),
            }
            for p in opponents
        ]
        opponent_card_events = []

    result: dict[str, Any] = {
        "session": session,
        "game": game_state,
        "you": you,
        "opponents": opponents_state,
        "waiting_for": _normalize_waiting_for(
            waiting_for, detail_level=normalized_detail_level
        ),
        "suggested_tools": _action_tools_for_input_type(input_type),
        "opponent_card_events": opponent_card_events,
    }

    if include_full_model:
        result["raw_player_model"] = player_model
    return result
