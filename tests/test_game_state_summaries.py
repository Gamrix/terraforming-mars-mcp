from __future__ import annotations

import importlib
from typing import Any

import terraforming_mars_mcp.card_info as card_info_mod
import terraforming_mars_mcp.game_state as game_state_mod
import terraforming_mars_mcp.server as server_mod
from terraforming_mars_mcp.api_response_models import PlayerViewModel


def _reload_server() -> Any:
    return importlib.reload(server_mod)


def _reload_card_info() -> Any:
    return importlib.reload(card_info_mod)


def test_get_game_state_surfaces_milestones_and_awards() -> None:
    server = _reload_server()
    player_model: dict[str, Any] = {
        "id": "player-1",
        "game": {
            "id": "game-1",
            "phase": "action",
            "generation": 4,
            "temperature": -20,
            "oxygenLevel": 6,
            "oceans": 3,
            "venusScaleLevel": 2,
            "isTerraformed": False,
            "gameAge": 123,
            "undoCount": 0,
            "passedPlayers": [],
            "spaces": [],
            "milestones": [
                {
                    "name": "Builder",
                    "playerName": "Alice",
                    "color": "red",
                    "scores": [
                        {"color": "red", "score": 8, "claimable": True},
                        {"color": "blue", "score": 6},
                    ],
                },
                {
                    "name": "Mayor",
                    "playerName": None,
                    "color": None,
                    "scores": [
                        {"color": "red", "score": 2},
                        {"color": "blue", "score": 3, "claimable": True},
                    ],
                },
            ],
            "awards": [
                {
                    "name": "Banker",
                    "playerName": "Bob",
                    "color": "blue",
                    "scores": [
                        {"color": "red", "score": 6},
                        {"color": "blue", "score": 8},
                    ],
                },
                {
                    "name": "Scientist",
                    "playerName": None,
                    "color": None,
                    "scores": [
                        {"color": "red", "score": 1},
                        {"color": "blue", "score": 0},
                    ],
                },
            ],
        },
        "players": [
            {"name": "Alice", "color": "red", "isActive": True},
            {"name": "Bob", "color": "blue", "isActive": False},
        ],
        "thisPlayer": {"name": "Alice", "color": "red", "isActive": True},
    }

    player_view = PlayerViewModel.model_validate(player_model)
    server._get_player = lambda player_id=None: player_view
    state = server.get_game_state()

    assert state["game"]["milestones"][0]["name"] == "Builder"
    assert state["game"]["milestones"][0]["status"] == "claimed"
    assert state["game"]["milestones"][0]["owner_name"] == "Alice"
    assert state["game"]["milestones"][0]["claimable_by"] == ["red"]
    assert state["game"]["milestones"][1]["status"] == "available"
    assert state["game"]["milestones"][1]["claimable_by"] == ["blue"]

    assert state["game"]["awards"][0]["name"] == "Banker"
    assert state["game"]["awards"][0]["status"] == "funded"
    assert state["game"]["awards"][0]["funder_name"] == "Bob"
    assert state["game"]["awards"][1]["status"] == "unfunded"


def test_get_my_hand_cards_returns_cards_in_hand() -> None:
    server = _reload_server()
    player_model: dict[str, Any] = {
        "id": "player-1",
        "game": {
            "id": "game-1",
            "phase": "action",
            "generation": 2,
            "temperature": -26,
            "oxygenLevel": 3,
            "oceans": 1,
            "venusScaleLevel": 0,
            "isTerraformed": False,
            "spaces": [],
        },
        "players": [{"name": "Alice", "color": "red", "isActive": True}],
        "thisPlayer": {"name": "Alice", "color": "red", "isActive": True},
        "cardsInHand": [
            {"name": "Comet", "calculatedCost": 21},
            {"name": "Asteroid", "calculatedCost": 14},
        ],
    }

    player_view = PlayerViewModel.model_validate(player_model)
    server._get_player = lambda player_id=None: player_view
    hand = server.get_my_hand_cards()

    assert hand["cards_in_hand_count"] == 2
    assert {card["name"] for card in hand["cards_in_hand"]} == {"Comet", "Asteroid"}
    assert all(isinstance(card["tags"], list) for card in hand["cards_in_hand"])
    assert all("cost" in card for card in hand["cards_in_hand"])


def _make_player_model(
    generation: int = 4,
    temperature: int = -20,
    oxygen: int = 6,
    oceans: int = 3,
    game_age: int = 123,
    phase: str = "action",
    waiting_for: dict[str, Any] | None = None,
    cards_in_hand: list[dict[str, Any]] | None = None,
    tableau: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    player: dict[str, Any] = {"name": "Alice", "color": "red", "isActive": True}
    if tableau is not None:
        player["tableau"] = tableau

    model: dict[str, Any] = {
        "id": "player-1",
        "game": {
            "id": "game-1",
            "phase": phase,
            "generation": generation,
            "temperature": temperature,
            "oxygenLevel": oxygen,
            "oceans": oceans,
            "venusScaleLevel": 0,
            "isTerraformed": False,
            "gameAge": game_age,
            "undoCount": 0,
            "passedPlayers": [],
            "spaces": [],
            "milestones": [],
            "awards": [],
        },
        "players": [player],
        "thisPlayer": dict(player),
    }
    if waiting_for is not None:
        model["waitingFor"] = waiting_for
    if cards_in_hand is not None:
        model["cardsInHand"] = cards_in_hand
    return model


def _make_two_player_model(
    generation: int = 4,
    game_age: int = 123,
    my_tableau: list[dict[str, Any]] | None = None,
    opponent_tableau: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    me: dict[str, Any] = {"name": "Alice", "color": "red", "isActive": True}
    opponent: dict[str, Any] = {"name": "Bob", "color": "blue", "isActive": False}
    if my_tableau is not None:
        me["tableau"] = my_tableau
    if opponent_tableau is not None:
        opponent["tableau"] = opponent_tableau

    return {
        "id": "player-1",
        "game": {
            "id": "game-1",
            "phase": "action",
            "generation": generation,
            "temperature": -20,
            "oxygenLevel": 6,
            "oceans": 3,
            "venusScaleLevel": 0,
            "isTerraformed": False,
            "gameAge": game_age,
            "undoCount": 0,
            "passedPlayers": [],
            "spaces": [],
            "milestones": [],
            "awards": [],
        },
        "players": [me, opponent],
        "thisPlayer": dict(me),
    }


def test_game_constants_sent_on_first_call_and_omitted_on_repeat() -> None:
    """Session and game constants are sent on first call, omitted on repeat."""
    server = _reload_server()
    importlib.reload(game_state_mod)

    raw = _make_player_model(generation=4, game_age=100)
    player_view = PlayerViewModel.model_validate(raw)
    server._get_player = lambda player_id=None: player_view

    # First call: constants are included.
    state1 = server.get_game_state()
    assert "session" in state1
    assert "phase" in state1["game"]
    assert "terraforming" in state1["game"]

    # Second call, same generation, same constants: omitted.
    raw2 = _make_player_model(generation=4, game_age=101)
    player_view2 = PlayerViewModel.model_validate(raw2)
    server._get_player = lambda player_id=None: player_view2

    state2 = server.get_game_state()
    assert "session" not in state2
    assert "phase" not in state2["game"]
    assert "terraforming" not in state2["game"]
    # Generation is always present for context.
    assert state2["game"]["generation"] == 4


def test_build_agent_state_reports_opponent_new_cards() -> None:
    importlib.reload(game_state_mod)

    raw1 = _make_two_player_model(game_age=100, opponent_tableau=[])
    player_view1 = PlayerViewModel.model_validate(raw1)
    state1 = game_state_mod._build_agent_state(player_view1, auto_response=True)
    assert state1.get("opponent_new_cards", []) == []

    raw2 = _make_two_player_model(
        game_age=101,
        opponent_tableau=[
            {"name": "Trans-Neptune Probe"},
            {"name": "Anti-Gravity Technology"},
        ],
    )
    player_view2 = PlayerViewModel.model_validate(raw2)
    state2 = game_state_mod._build_agent_state(player_view2, auto_response=True)

    assert [card["card_name"] for card in state2["opponent_new_cards"]] == [
        "Trans-Neptune Probe",
        "Anti-Gravity Technology",
    ]
    assert all(card["player_name"] == "Bob" for card in state2["opponent_new_cards"])


def test_game_constants_resent_on_generation_change() -> None:
    """Constants are re-sent when the generation changes."""
    server = _reload_server()
    importlib.reload(game_state_mod)

    raw_gen4 = _make_player_model(generation=4, game_age=100)
    player_view4 = PlayerViewModel.model_validate(raw_gen4)
    server._get_player = lambda player_id=None: player_view4

    # Prime the tracker.
    server.get_game_state()

    # New generation: constants should reappear.
    raw_gen5 = _make_player_model(generation=5, game_age=200)
    player_view5 = PlayerViewModel.model_validate(raw_gen5)
    server._get_player = lambda player_id=None: player_view5

    state = server.get_game_state()
    assert "session" in state
    assert "phase" in state["game"]
    assert "terraforming" in state["game"]
    assert state["game"]["generation"] == 5


def test_game_constants_resent_on_value_change_within_generation() -> None:
    """Constants are re-sent when a value changes even within the same gen."""
    server = _reload_server()
    importlib.reload(game_state_mod)

    raw = _make_player_model(generation=4, temperature=-20, game_age=100)
    player_view = PlayerViewModel.model_validate(raw)
    server._get_player = lambda player_id=None: player_view

    server.get_game_state()

    # Temperature changed within same generation.
    raw2 = _make_player_model(generation=4, temperature=-18, game_age=101)
    player_view2 = PlayerViewModel.model_validate(raw2)
    server._get_player = lambda player_id=None: player_view2

    state = server.get_game_state()
    assert "session" in state
    assert "terraforming" in state["game"]
    assert state["game"]["terraforming"]["temperature"] == -18


def test_you_and_opponents_omitted_between_intervals() -> None:
    """you/opponents are included at gen start and every N responses, omitted otherwise."""
    server = _reload_server()
    importlib.reload(game_state_mod)

    raw = _make_player_model(generation=4, game_age=100)
    player_view = PlayerViewModel.model_validate(raw)
    server._get_player = lambda player_id=None: player_view
    first = server.get_game_state()
    # First call in a new generation → included
    assert "you" in first

    raw2 = _make_player_model(generation=4, game_age=101)
    player_view2 = PlayerViewModel.model_validate(raw2)
    server._get_player = lambda player_id=None: player_view2
    second = server.get_game_state()
    # Same generation, not yet at interval → omitted
    assert "you" not in second

    # Advance to next generation → included again
    raw3 = _make_player_model(generation=5, game_age=120)
    player_view3 = PlayerViewModel.model_validate(raw3)
    server._get_player = lambda player_id=None: player_view3
    third = server.get_game_state()
    assert "you" in third


def test_proactive_calls_always_return_full_card_details() -> None:
    """Proactive get_game_state calls always return full card details."""
    server = _reload_server()
    importlib.reload(game_state_mod)
    _reload_card_info()
    card_info_mod._CARD_TRACKER.reset()

    waiting_for = {
        "type": "card",
        "title": "Select",
        "buttonLabel": "Save",
        "min": 1,
        "max": 1,
        "cards": [{"name": "Comet", "calculatedCost": 21}],
    }
    raw = _make_player_model(generation=4, game_age=100, waiting_for=waiting_for)
    player_view = PlayerViewModel.model_validate(raw)
    server._get_player = lambda player_id=None: player_view

    # First proactive call: full details.
    state1 = server.get_game_state()
    card1 = state1["waiting_for"]["cards"][0]
    assert card1["name"] == "Comet"
    assert "tags" in card1
    assert "effect_texts" in card1

    # Second proactive call same gen: still full details (proactive = no caching).
    raw2 = _make_player_model(generation=4, game_age=101, waiting_for=waiting_for)
    player_view2 = PlayerViewModel.model_validate(raw2)
    server._get_player = lambda player_id=None: player_view2

    state2 = server.get_game_state()
    card2 = state2["waiting_for"]["cards"][0]
    assert card2["name"] == "Comet"
    assert "tags" in card2
    assert "effect_texts" in card2


def test_auto_response_returns_name_only_on_repeat() -> None:
    """Auto-returned responses reduce to name-only after first appearance."""
    importlib.reload(game_state_mod)
    _reload_card_info()
    card_info_mod._CARD_TRACKER.reset()

    waiting_for = {
        "type": "card",
        "title": "Select",
        "buttonLabel": "Save",
        "min": 1,
        "max": 1,
        "cards": [{"name": "Comet", "calculatedCost": 21}],
    }

    # First auto-response: full details.
    raw = _make_player_model(generation=4, game_age=100, waiting_for=waiting_for)
    player_view = PlayerViewModel.model_validate(raw)
    state1 = game_state_mod._build_agent_state(player_view, auto_response=True)
    card1 = state1["waiting_for"]["cards"][0]
    assert card1["name"] == "Comet"
    assert "tags" in card1
    assert "effect_texts" in card1

    # Second auto-response same gen: name only.
    raw2 = _make_player_model(generation=4, game_age=101, waiting_for=waiting_for)
    player_view2 = PlayerViewModel.model_validate(raw2)
    state2 = game_state_mod._build_agent_state(player_view2, auto_response=True)
    card2 = state2["waiting_for"]["cards"][0]
    assert card2 == {"name": "Comet"}


def test_auto_response_resends_on_warning_change() -> None:
    """Auto-returned responses re-send details when dynamic fields change."""
    importlib.reload(game_state_mod)
    _reload_card_info()
    card_info_mod._CARD_TRACKER.reset()

    wf1 = {
        "type": "card",
        "title": "Select",
        "buttonLabel": "Save",
        "min": 1,
        "max": 1,
        "cards": [{"name": "Comet", "calculatedCost": 21}],
    }
    raw = _make_player_model(generation=4, game_age=100, waiting_for=wf1)
    player_view = PlayerViewModel.model_validate(raw)
    game_state_mod._build_agent_state(player_view, auto_response=True)

    # Same card now has a warning — should re-send details.
    wf2 = {
        "type": "card",
        "title": "Select",
        "buttonLabel": "Save",
        "min": 1,
        "max": 1,
        "cards": [
            {"name": "Comet", "calculatedCost": 21, "warnings": ["maxoceans"]},
        ],
    }
    raw2 = _make_player_model(generation=4, game_age=101, waiting_for=wf2)
    player_view2 = PlayerViewModel.model_validate(raw2)
    state2 = game_state_mod._build_agent_state(player_view2, auto_response=True)
    card2 = state2["waiting_for"]["cards"][0]
    assert card2["name"] == "Comet"
    assert "tags" in card2
    assert card2["warnings"] == ["maxoceans"]


def test_auto_response_resets_on_new_generation() -> None:
    """Auto-returned card details reset when the generation changes."""
    importlib.reload(game_state_mod)
    _reload_card_info()
    card_info_mod._CARD_TRACKER.reset()

    waiting_for = {
        "type": "card",
        "title": "Select",
        "buttonLabel": "Save",
        "min": 1,
        "max": 1,
        "cards": [{"name": "Comet", "calculatedCost": 21}],
    }

    # Gen 4: prime the tracker with auto-response.
    raw4 = _make_player_model(generation=4, game_age=100, waiting_for=waiting_for)
    player_view4 = PlayerViewModel.model_validate(raw4)
    game_state_mod._build_agent_state(player_view4, auto_response=True)

    # Gen 5: same card, full details should reappear.
    raw5 = _make_player_model(generation=5, game_age=200, waiting_for=waiting_for)
    player_view5 = PlayerViewModel.model_validate(raw5)
    state = game_state_mod._build_agent_state(player_view5, auto_response=True)
    card = state["waiting_for"]["cards"][0]
    assert card["name"] == "Comet"
    assert "tags" in card
    assert "effect_texts" in card


def test_auto_response_includes_generation_start_context_on_new_generation(
    monkeypatch,
) -> None:
    importlib.reload(game_state_mod)
    _reload_card_info()
    card_info_mod._CARD_TRACKER.reset()

    def fake_card_info(
        card_name: str, include_play_details: bool = False
    ) -> dict[str, object]:
        assert include_play_details is True
        if card_name == "Comet":
            return {
                "name": card_name,
                "tags": ["space"],
                "ongoing_effects": [],
                "activated_actions": [],
                "play_requirements": [],
                "play_requirements_text": None,
                "on_play_effect_text": "Raise temperature 1 step.",
                "base_cost": 21,
            }
        if card_name == "Asteroid":
            return {
                "name": card_name,
                "tags": ["space", "event"],
                "ongoing_effects": [],
                "activated_actions": [],
                "play_requirements": [],
                "play_requirements_text": None,
                "on_play_effect_text": "Raise temperature 2 steps.",
                "base_cost": 14,
            }
        if card_name == "Media Group":
            return {
                "name": card_name,
                "tags": ["earth"],
                "ongoing_effects": ["Effect: Gain 3 MC when you play an event card."],
                "activated_actions": [],
                "play_requirements": [],
                "play_requirements_text": None,
                "on_play_effect_text": None,
                "base_cost": 6,
            }
        if card_name == "Inventors' Guild":
            return {
                "name": card_name,
                "tags": ["science"],
                "ongoing_effects": [],
                "activated_actions": [
                    "Action: Look at the top card and either buy it or discard it."
                ],
                "play_requirements": [],
                "play_requirements_text": None,
                "on_play_effect_text": None,
                "base_cost": 9,
            }
        return {
            "name": card_name,
            "tags": [],
            "ongoing_effects": [],
            "activated_actions": [],
            "play_requirements": [],
            "play_requirements_text": None,
            "on_play_effect_text": None,
            "base_cost": 0,
        }

    monkeypatch.setattr("terraforming_mars_mcp.card_info._card_info", fake_card_info)

    raw4 = _make_player_model(generation=4, game_age=100)
    player_view4 = PlayerViewModel.model_validate(raw4)
    game_state_mod._build_agent_state(player_view4, auto_response=True)

    raw5 = _make_player_model(
        generation=5,
        game_age=200,
        cards_in_hand=[
            {"name": "Comet", "calculatedCost": 21},
            {"name": "Asteroid", "calculatedCost": 14},
        ],
        tableau=[
            {"name": "Media Group", "calculatedCost": 6},
            {"name": "Inventors' Guild", "calculatedCost": 9},
        ],
    )
    player_view5 = PlayerViewModel.model_validate(raw5)
    state = game_state_mod._build_agent_state(player_view5, auto_response=True)

    generation_start = state["generation_start"]
    assert generation_start["cards_in_hand_count"] == 2
    assert [card["name"] for card in generation_start["cards_in_hand"]] == [
        "Comet",
        "Asteroid",
    ]
    assert generation_start["played_card_effects_and_actions"] == [
        {
            "name": "Media Group",
            "effect_texts": ["Effect: Gain 3 MC when you play an event card."],
        },
        {
            "name": "Inventors' Guild",
            "action_texts": [
                "Action: Look at the top card and either buy it or discard it."
            ],
        },
    ]

    raw5_repeat = _make_player_model(
        generation=5,
        game_age=201,
        cards_in_hand=[
            {"name": "Comet", "calculatedCost": 21},
            {"name": "Asteroid", "calculatedCost": 14},
        ],
        tableau=[
            {"name": "Media Group", "calculatedCost": 6},
            {"name": "Inventors' Guild", "calculatedCost": 9},
        ],
    )
    player_view5_repeat = PlayerViewModel.model_validate(raw5_repeat)
    repeat_state = game_state_mod._build_agent_state(
        player_view5_repeat, auto_response=True
    )
    assert "generation_start" not in repeat_state


def test_disabled_cards_are_filtered_out() -> None:
    """Disabled cards are filtered out of the card list entirely."""
    server = _reload_server()
    importlib.reload(game_state_mod)
    _reload_card_info()
    card_info_mod._CARD_TRACKER.reset()

    waiting_for = {
        "type": "card",
        "title": "Standard projects",
        "buttonLabel": "Confirm",
        "min": 1,
        "max": 1,
        "cards": [
            {"name": "Comet", "calculatedCost": 21, "isDisabled": False},
            {"name": "Asteroid", "calculatedCost": 14, "isDisabled": True},
        ],
    }
    raw = _make_player_model(generation=4, game_age=100, waiting_for=waiting_for)
    player_view = PlayerViewModel.model_validate(raw)
    server._get_player = lambda player_id=None: player_view

    state = server.get_game_state()
    cards = state["waiting_for"]["cards"]

    # Only enabled cards remain after filtering.
    assert len(cards) == 1
    assert cards[0]["name"] == "Comet"
    assert "cost" in cards[0]
    assert "tags" in cards[0]
    assert "disabled" not in cards[0]


def test_auto_response_all_disabled_cards_produce_empty_list() -> None:
    """When all cards are disabled, the filtered list is empty."""
    importlib.reload(game_state_mod)
    _reload_card_info()
    card_info_mod._CARD_TRACKER.reset()

    waiting_for = {
        "type": "card",
        "title": "Standard projects",
        "buttonLabel": "Confirm",
        "min": 1,
        "max": 1,
        "cards": [
            {"name": "Asteroid", "calculatedCost": 14, "isDisabled": True},
        ],
    }
    raw = _make_player_model(generation=4, game_age=100, waiting_for=waiting_for)
    player_view = PlayerViewModel.model_validate(raw)
    state = game_state_mod._build_agent_state(player_view, auto_response=True)
    assert "cards" not in state["waiting_for"]


def test_opponent_new_cards_have_no_none_or_empty_list_fields() -> None:
    """opponent_new_cards dicts should not contain None values or empty lists."""
    importlib.reload(game_state_mod)

    raw1 = _make_two_player_model(game_age=100, opponent_tableau=[])
    player_view1 = PlayerViewModel.model_validate(raw1)
    game_state_mod._build_agent_state(player_view1, auto_response=True)

    # Sponsors has no ongoing_effects, no activated_actions, no play_requirements_text.
    raw2 = _make_two_player_model(game_age=101, opponent_tableau=[{"name": "Sponsors"}])
    player_view2 = PlayerViewModel.model_validate(raw2)
    state = game_state_mod._build_agent_state(player_view2, auto_response=True)

    cards = state["opponent_new_cards"]
    assert len(cards) == 1
    card = cards[0]
    for key, value in card.items():
        assert value is not None, f"{key} should not be None"
        assert value != [], f"{key} should not be empty list"
