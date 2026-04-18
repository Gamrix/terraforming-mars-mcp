"""Additional MCP tool handlers (untested action tools)."""

from __future__ import annotations

import json
from typing import Any, cast

from ._app import mcp
from ._models import (
    InitialCardsSelectionModel,
    PaymentPayloadModel,
    RawInputEntityRequest,
    UnitsPayloadModel,
    normalize_raw_input_entity,
)
from .api_response_models import JsonValue
from .card_info import extract_played_cards
from .game_state import build_agent_state, full_board_state
from .turn_flow import (
    CFG,
    _get_game_logs,
    _post_input,
    get_player,
    submit_and_return_state,
    wait_for_turn_from_player_model,
)


@mcp.tool()
def get_opponents_played_cards() -> dict[str, object]:
    """Return all cards currently in each opponent's tableau (played cards)."""
    player_model = get_player()
    this_color = player_model.thisPlayer.color

    opponents: list[dict[str, object]] = []
    for player in player_model.players:
        if player.color == this_color:
            continue
        played_cards = extract_played_cards(player)
        opponents.append(
            {
                "name": player.name,
                "color": player.color,
                "played_cards_count": len(played_cards),
                "played_cards": played_cards,
            }
        )

    game = player_model.game
    return {
        "generation": game.generation,
        "phase": game.phase,
        "opponents": opponents,
    }


@mcp.tool()
def get_my_played_cards() -> dict[str, object]:
    """Return all cards currently in your tableau (played cards)."""
    player_model = get_player()
    this_player = player_model.thisPlayer
    cards = extract_played_cards(this_player)
    game = player_model.game
    return {
        "generation": game.generation,
        "phase": game.phase,
        "player": this_player.name,
        "color": this_player.color,
        "played_cards_count": len(cards),
        "played_cards": cards,
    }


@mcp.tool()
def get_mars_board_state(include_empty_spaces: bool = False) -> dict[str, object]:
    """Return detailed Mars board state. This is the explicit board-inspection tool."""
    player_model = get_player()
    return full_board_state(
        player_model.game, include_empty_spaces=include_empty_spaces
    )


@mcp.tool()
async def wait_for_turn() -> dict[str, Any]:
    """Poll /api/waitingfor until it's your turn using fixed server defaults."""
    player_model = get_player()
    if player_model.waitingFor is not None:
        return {
            "status": "GO",
            "state": build_agent_state(
                player_model, base_url=CFG.base_url, player_id_fallback=CFG.player_id
            ),
        }
    refreshed, opponent_actions = await wait_for_turn_from_player_model(player_model)
    state = build_agent_state(
        refreshed,
        base_url=CFG.base_url,
        player_id_fallback=CFG.player_id,
        between_turns_actions=opponent_actions,
    )
    return {"status": "GO", "state": state}


@mcp.tool()
async def submit_raw_entity(request: RawInputEntityRequest) -> dict[str, object]:
    """Submit any raw /player/input payload as a JSON object with `type`."""
    entity = json.loads(request.entity_json)
    if not isinstance(entity, dict):
        raise ValueError("entity_json must decode to an object")
    if "type" not in entity:
        raise ValueError("entity_json must include a 'type' field")
    return await submit_and_return_state(
        normalize_raw_input_entity(cast(dict[str, object], entity))
    )


@mcp.tool()
async def submit_and_options(responses_json: str) -> dict[str, object]:
    """Respond to `type: and` with JSON list of InputResponse objects."""
    responses = json.loads(responses_json)
    if not isinstance(responses, list):
        raise ValueError("responses_json must decode to a list of objects")
    normalized_responses: list[dict[str, JsonValue]] = []
    for item in responses:
        if not isinstance(item, dict):
            raise ValueError("Each response must be an object")
        normalized_responses.append(cast(dict[str, JsonValue], item))
    return await submit_and_return_state(
        {"type": "and", "responses": cast(JsonValue, normalized_responses)}
    )


@mcp.tool()
async def submit_turn_actions(actions_json: str) -> dict[str, object]:
    """Submit a sequence of actions for your entire turn in one call.

    Each action is submitted to the server in order. After each submission,
    if the server requests more input (select a space, choose resources, etc.),
    the next action in the list is used as the response. Continues until all
    actions are consumed or the turn ends.

    actions_json: JSON array of InputResponse objects, each with a `type` field.
    These are the same raw payloads you would pass to submit_raw_entity.

    Example — play a card that needs space selection, then pass:
    [
        {"type": "or", "index": 0, "response": {"type": "projectCard", "card": "Noctis City", "payment": {"megaCredits": 20}}},
        {"type": "space", "spaceId": "35"},
        {"type": "or", "index": 5, "response": {"type": "option"}}
    ]
    """
    actions = json.loads(actions_json)
    if not isinstance(actions, list):
        raise ValueError("actions_json must decode to a JSON array")
    if len(actions) == 0:
        raise ValueError("actions_json must contain at least one action")

    player_model = None
    actions_executed = 0
    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            raise ValueError(f"Action at index {i} must be a JSON object")
        if "type" not in action:
            raise ValueError(f"Action at index {i} must include a 'type' field")

        normalized = normalize_raw_input_entity(cast(dict[str, object], action))
        player_model = _post_input(cast(dict[str, JsonValue], normalized))
        actions_executed += 1

        if player_model.waitingFor is None and actions_executed < len(actions):
            break

    assert player_model is not None

    if player_model.waitingFor is None:
        initial_logs = _get_game_logs()
        refreshed, opponent_actions = await wait_for_turn_from_player_model(
            player_model, initial_logs=initial_logs
        )
        result = build_agent_state(
            refreshed,
            base_url=CFG.base_url,
            player_id_fallback=CFG.player_id,
            auto_response=True,
            between_turns_actions=opponent_actions,
        )
    else:
        result = build_agent_state(
            player_model,
            base_url=CFG.base_url,
            player_id_fallback=CFG.player_id,
            auto_response=True,
        )

    result["actions_executed"] = actions_executed
    return result


@mcp.tool()
async def select_amount(amount: int) -> dict[str, object]:
    """Respond to `type: amount`."""
    return await submit_and_return_state({"type": "amount", "amount": int(amount)})


@mcp.tool()
async def select_cards(card_names: list[str]) -> dict[str, object]:
    """Respond to `type: card` with chosen card names."""
    return await submit_and_return_state(
        {"type": "card", "cards": cast(JsonValue, card_names)}
    )


@mcp.tool()
async def select_player(player_color: str) -> dict[str, object]:
    """Respond to `type: player`."""
    if not player_color:
        raise ValueError("player_color is required")
    return await submit_and_return_state({"type": "player", "player": player_color})


@mcp.tool()
async def select_delegate_target(player_color_or_neutral: str) -> dict[str, object]:
    """Respond to `type: delegate` with a player color or `NEUTRAL`."""
    if not player_color_or_neutral:
        raise ValueError("player_color_or_neutral is required")
    return await submit_and_return_state(
        {"type": "delegate", "player": player_color_or_neutral}
    )


@mcp.tool()
async def select_space(space_id: str) -> dict[str, object]:
    """Respond to `type: space` using a board space ID from `waiting_for.spaces`."""
    if not space_id:
        raise ValueError("space_id is required")
    return await submit_and_return_state({"type": "space", "spaceId": space_id})


@mcp.tool()
async def select_party(party_name: str) -> dict[str, object]:
    """Respond to `type: party`."""
    if not party_name:
        raise ValueError("party_name is required")
    return await submit_and_return_state({"type": "party", "partyName": party_name})


@mcp.tool()
async def select_colony(colony_name: str) -> dict[str, object]:
    """Respond to `type: colony`."""
    if not colony_name:
        raise ValueError("colony_name is required")
    return await submit_and_return_state({"type": "colony", "colonyName": colony_name})


@mcp.tool()
async def pay_for_action(
    payment: PaymentPayloadModel = PaymentPayloadModel(),
) -> dict[str, object]:
    """Respond to `type: payment`."""
    return await submit_and_return_state(
        {"type": "payment", "payment": payment.model_dump(by_alias=True)}
    )


@mcp.tool()
async def select_initial_cards(
    request: InitialCardsSelectionModel,
) -> dict[str, object]:
    """Respond to `type: initialCards` using current waiting-for option order."""
    player_model = get_player()
    waiting_for = player_model.waitingFor
    options = waiting_for.options if waiting_for is not None else None
    if not isinstance(options, list):
        raise RuntimeError("Current waitingFor has no options for initialCards")

    responses: list[dict[str, JsonValue]] = []
    for option in options:
        title_text = (
            option.title if isinstance(option.title, str) else option.title.message
        )
        title = title_text.lower()
        if "corporation" in title:
            cards = [request.corporation_card] if request.corporation_card else []
        elif "prelude" in title:
            cards = request.prelude_cards
        elif "ceo" in title:
            cards = request.ceo_cards
        else:
            cards = request.project_cards
        responses.append({"type": "card", "cards": cast(JsonValue, cards)})

    return await submit_and_return_state(
        {"type": "initialCards", "responses": cast(JsonValue, responses)}
    )


@mcp.tool()
async def select_production_to_lose(
    units: UnitsPayloadModel = UnitsPayloadModel(),
) -> dict[str, object]:
    """Respond to `type: productionToLose`."""
    return await submit_and_return_state(
        {"type": "productionToLose", "units": units.model_dump()}
    )


@mcp.tool()
async def shift_ares_global_parameters(
    low_ocean_delta: int = 0,
    high_ocean_delta: int = 0,
    temperature_delta: int = 0,
    oxygen_delta: int = 0,
) -> dict[str, object]:
    """Respond to `type: aresGlobalParameters`. Values are expected in {-1,0,1}."""
    return await submit_and_return_state(
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
async def select_global_event(global_event_name: str) -> dict[str, object]:
    """Respond to `type: globalEvent`."""
    if not global_event_name:
        raise ValueError("global_event_name is required")
    return await submit_and_return_state(
        {"type": "globalEvent", "globalEventName": global_event_name}
    )


@mcp.tool()
async def select_policy(policy_id: str) -> dict[str, object]:
    """Respond to `type: policy`."""
    if not policy_id:
        raise ValueError("policy_id is required")
    return await submit_and_return_state({"type": "policy", "policyId": policy_id})


@mcp.tool()
async def select_resource(resource: str) -> dict[str, object]:
    """Respond to `type: resource`."""
    if not resource:
        raise ValueError("resource is required")
    return await submit_and_return_state({"type": "resource", "resource": resource})


@mcp.tool()
async def select_resources(
    units: UnitsPayloadModel = UnitsPayloadModel(),
) -> dict[str, object]:
    """Respond to `type: resources`."""
    return await submit_and_return_state(
        {"type": "resources", "units": units.model_dump()}
    )


@mcp.tool()
async def select_claimed_underground_tokens(selected: list[int]) -> dict[str, object]:
    """Respond to `type: claimedUndergroundToken`."""
    return await submit_and_return_state(
        {"type": "claimedUndergroundToken", "selected": cast(JsonValue, selected)}
    )
