"""Additional MCP tool handlers (untested action tools)."""

from __future__ import annotations

from typing import Any

try:
    from ._app import mcp
    from ._models import (
        InitialCardsSelectionModel,
        RawInputEntityRequest,
        _normalize_raw_input_entity,
    )
    from .api_response_models import WaitingForInputModel as ApiWaitingForInputModel
    from .card_info import _extract_played_cards
    from .game_state import _build_agent_state, _full_board_state
    from .turn_flow import (
        CFG,
        _get_player,
        _has_waiting_input,
        _submit_and_return_state,
        _wait_for_turn_from_player_model,
    )
    from .waiting_for import _get_waiting_for_model
except ImportError:
    from _app import mcp  # type: ignore[no-redef]
    from _models import (
        InitialCardsSelectionModel,
        RawInputEntityRequest,
        _normalize_raw_input_entity,
    )  # type: ignore[no-redef]
    from api_response_models import WaitingForInputModel as ApiWaitingForInputModel  # type: ignore[no-redef]
    from card_info import _extract_played_cards  # type: ignore[no-redef]
    from game_state import _build_agent_state, _full_board_state  # type: ignore[no-redef]
    from turn_flow import (  # type: ignore[no-redef]
        CFG,
        _get_player,
        _has_waiting_input,
        _submit_and_return_state,
        _wait_for_turn_from_player_model,
    )
    from waiting_for import _get_waiting_for_model  # type: ignore[no-redef]


@mcp.tool()
def get_opponents_played_cards() -> dict[str, Any]:
    """Return all cards currently in each opponent's tableau (played cards)."""
    player_model = _get_player()
    this_player = player_model.get("thisPlayer")
    this_color = this_player.get("color") if isinstance(this_player, dict) else None
    players = player_model.get("players")

    opponents: list[dict[str, Any]] = []
    if isinstance(players, list):
        for player in players:
            if not isinstance(player, dict):
                continue
            if player.get("color") == this_color:
                continue
            played_cards = _extract_played_cards(player, include_play_details=True)
            opponents.append(
                {
                    "name": player.get("name"),
                    "color": player.get("color"),
                    "played_cards_count": len(played_cards),
                    "played_cards": played_cards,
                }
            )

    game = (
        player_model.get("game", {})
        if isinstance(player_model.get("game"), dict)
        else {}
    )
    return {
        "generation": game.get("generation"),
        "phase": game.get("phase"),
        "opponents": opponents,
    }


@mcp.tool()
def get_my_played_cards() -> dict[str, Any]:
    """Return all cards currently in your tableau (played cards)."""
    player_model = _get_player()
    this_player = player_model.get("thisPlayer")
    if not isinstance(this_player, dict):
        raise RuntimeError("Missing thisPlayer in /api/player response")

    cards = _extract_played_cards(this_player)
    game = (
        player_model.get("game", {})
        if isinstance(player_model.get("game"), dict)
        else {}
    )
    return {
        "generation": game.get("generation"),
        "phase": game.get("phase"),
        "player": this_player.get("name"),
        "color": this_player.get("color"),
        "played_cards_count": len(cards),
        "played_cards": cards,
    }


@mcp.tool()
def get_mars_board_state(include_empty_spaces: bool = False) -> dict[str, Any]:
    """Return detailed Mars board state. This is the explicit board-inspection tool."""
    player_model = _get_player()
    game = player_model.get("game", {})
    if not isinstance(game, dict):
        raise RuntimeError("Missing game object in /api/player response")
    return _full_board_state(game, include_empty_spaces=include_empty_spaces)


@mcp.tool()
def wait_for_turn() -> dict[str, Any]:
    """Poll /api/waitingfor until it's your turn using fixed server defaults."""
    player_model = _get_player()
    if _has_waiting_input(player_model):
        return {
            "status": "GO",
            "state": _build_agent_state(
                player_model, base_url=CFG.base_url, player_id_fallback=CFG.player_id
            ),
        }
    refreshed, opponent_actions = _wait_for_turn_from_player_model(player_model)
    result = {
        "status": "GO",
        "state": _build_agent_state(
            refreshed, base_url=CFG.base_url, player_id_fallback=CFG.player_id
        ),
    }
    if opponent_actions:
        result["opponent_actions_between_turns"] = opponent_actions
    return result


@mcp.tool()
def submit_raw_entity(request: RawInputEntityRequest) -> dict[str, Any]:
    """Submit any raw /player/input payload as a JSON object with `type`."""
    import json as _json

    entity = _json.loads(request.entity_json)
    if not isinstance(entity, dict):
        raise ValueError("entity_json must decode to an object")
    if "type" not in entity:
        raise ValueError("entity_json must include a 'type' field")
    return _submit_and_return_state(_normalize_raw_input_entity(entity))


@mcp.tool()
def submit_and_options(responses_json: str) -> dict[str, Any]:
    """Respond to `type: and` with JSON list of InputResponse objects."""
    import json as _json

    responses = _json.loads(responses_json)
    if not isinstance(responses, list):
        raise ValueError("responses_json must decode to a list of objects")
    for item in responses:
        if not isinstance(item, dict):
            raise ValueError("Each response must be an object")
    return _submit_and_return_state({"type": "and", "responses": responses})


@mcp.tool()
def select_amount(amount: int) -> dict[str, Any]:
    """Respond to `type: amount`."""
    return _submit_and_return_state({"type": "amount", "amount": int(amount)})


@mcp.tool()
def select_cards(card_names: list[str]) -> dict[str, Any]:
    """Respond to `type: card` with chosen card names."""
    return _submit_and_return_state({"type": "card", "cards": card_names})


@mcp.tool()
def select_player(player_color: str) -> dict[str, Any]:
    """Respond to `type: player`."""
    if not player_color:
        raise ValueError("player_color is required")
    return _submit_and_return_state({"type": "player", "player": player_color})


@mcp.tool()
def select_delegate_target(player_color_or_neutral: str) -> dict[str, Any]:
    """Respond to `type: delegate` with a player color or `NEUTRAL`."""
    if not player_color_or_neutral:
        raise ValueError("player_color_or_neutral is required")
    return _submit_and_return_state(
        {"type": "delegate", "player": player_color_or_neutral}
    )


@mcp.tool()
def select_space(space_id: str) -> dict[str, Any]:
    """Respond to `type: space` using a board space ID from `waiting_for.spaces`."""
    if not space_id:
        raise ValueError("space_id is required")
    return _submit_and_return_state({"type": "space", "spaceId": space_id})


@mcp.tool()
def select_party(party_name: str) -> dict[str, Any]:
    """Respond to `type: party`."""
    if not party_name:
        raise ValueError("party_name is required")
    return _submit_and_return_state({"type": "party", "partyName": party_name})


@mcp.tool()
def select_colony(colony_name: str) -> dict[str, Any]:
    """Respond to `type: colony`."""
    if not colony_name:
        raise ValueError("colony_name is required")
    return _submit_and_return_state({"type": "colony", "colonyName": colony_name})


@mcp.tool()
def pay_for_action(
    mega_credits: int = 0,
    steel: int = 0,
    titanium: int = 0,
    heat: int = 0,
    plants: int = 0,
    microbes: int = 0,
    floaters: int = 0,
    luna_archives_science: int = 0,
    spire_science: int = 0,
    seeds: int = 0,
    aurorai_data: int = 0,
    graphene: int = 0,
    kuiper_asteroids: int = 0,
) -> dict[str, Any]:
    """Respond to `type: payment`."""
    return _submit_and_return_state(
        {
            "type": "payment",
            "payment": {
                "megaCredits": mega_credits,
                "steel": steel,
                "titanium": titanium,
                "heat": heat,
                "plants": plants,
                "microbes": microbes,
                "floaters": floaters,
                "lunaArchivesScience": luna_archives_science,
                "spireScience": spire_science,
                "seeds": seeds,
                "auroraiData": aurorai_data,
                "graphene": graphene,
                "kuiperAsteroids": kuiper_asteroids,
            },
        }
    )


@mcp.tool()
def select_initial_cards(request: InitialCardsSelectionModel) -> dict[str, Any]:
    """Respond to `type: initialCards` using current waiting-for option order."""
    player_model = _get_player()
    waiting_for = _get_waiting_for_model(player_model)
    options = waiting_for.options if waiting_for is not None else None
    if not isinstance(options, list):
        raise RuntimeError("Current waitingFor has no options for initialCards")

    responses: list[dict[str, Any]] = []
    for option in options:
        if not isinstance(option, ApiWaitingForInputModel):
            raise RuntimeError("Invalid option in initialCards")
        title = str(option.title or "").lower()
        if "corporation" in title:
            cards = [request.corporation_card] if request.corporation_card else []
        elif "prelude" in title:
            cards = request.prelude_cards
        elif "ceo" in title:
            cards = request.ceo_cards
        else:
            cards = request.project_cards
        responses.append({"type": "card", "cards": cards})

    return _submit_and_return_state({"type": "initialCards", "responses": responses})


@mcp.tool()
def select_production_to_lose(
    megacredits: int = 0,
    steel: int = 0,
    titanium: int = 0,
    plants: int = 0,
    energy: int = 0,
    heat: int = 0,
) -> dict[str, Any]:
    """Respond to `type: productionToLose`."""
    return _submit_and_return_state(
        {
            "type": "productionToLose",
            "units": {
                "megacredits": megacredits,
                "steel": steel,
                "titanium": titanium,
                "plants": plants,
                "energy": energy,
                "heat": heat,
            },
        }
    )


@mcp.tool()
def shift_ares_global_parameters(
    low_ocean_delta: int = 0,
    high_ocean_delta: int = 0,
    temperature_delta: int = 0,
    oxygen_delta: int = 0,
) -> dict[str, Any]:
    """Respond to `type: aresGlobalParameters`. Values are expected in {-1,0,1}."""
    return _submit_and_return_state(
        {
            "type": "aresGlobalParameters",
            "response": {
                "lowOceanDelta": low_ocean_delta,
                "highOceanDelta": high_ocean_delta,
                "temperatureDelta": temperature_delta,
                "oxygenDelta": oxygen_delta,
            },
        }
    )


@mcp.tool()
def select_global_event(global_event_name: str) -> dict[str, Any]:
    """Respond to `type: globalEvent`."""
    if not global_event_name:
        raise ValueError("global_event_name is required")
    return _submit_and_return_state(
        {"type": "globalEvent", "globalEventName": global_event_name}
    )


@mcp.tool()
def select_policy(policy_id: str) -> dict[str, Any]:
    """Respond to `type: policy`."""
    if not policy_id:
        raise ValueError("policy_id is required")
    return _submit_and_return_state({"type": "policy", "policyId": policy_id})


@mcp.tool()
def select_resource(resource: str) -> dict[str, Any]:
    """Respond to `type: resource`."""
    if not resource:
        raise ValueError("resource is required")
    return _submit_and_return_state({"type": "resource", "resource": resource})


@mcp.tool()
def select_resources(
    megacredits: int = 0,
    steel: int = 0,
    titanium: int = 0,
    plants: int = 0,
    energy: int = 0,
    heat: int = 0,
) -> dict[str, Any]:
    """Respond to `type: resources`."""
    return _submit_and_return_state(
        {
            "type": "resources",
            "units": {
                "megacredits": megacredits,
                "steel": steel,
                "titanium": titanium,
                "plants": plants,
                "energy": energy,
                "heat": heat,
            },
        }
    )


@mcp.tool()
def select_claimed_underground_tokens(selected: list[int]) -> dict[str, Any]:
    """Respond to `type: claimedUndergroundToken`."""
    return _submit_and_return_state(
        {"type": "claimedUndergroundToken", "selected": selected}
    )
