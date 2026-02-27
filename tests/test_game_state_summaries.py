from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def _load_server_module() -> Any:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    module = importlib.import_module("terraforming_mars_mcp.server")
    return importlib.reload(module)


def test_get_game_state_surfaces_milestones_and_awards() -> None:
    server = _load_server_module()
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
                        {"color": "blue", "score": 6, "claimable": False},
                    ],
                },
                {
                    "name": "Mayor",
                    "playerName": None,
                    "color": None,
                    "scores": [
                        {"color": "red", "score": 2, "claimable": False},
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

    player_view = importlib.import_module(
        "terraforming_mars_mcp.api_response_models"
    ).PlayerViewModel.model_validate(player_model)
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
    server = _load_server_module()
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

    player_view = importlib.import_module(
        "terraforming_mars_mcp.api_response_models"
    ).PlayerViewModel.model_validate(player_model)
    server._get_player = lambda player_id=None: player_view
    hand = server.get_my_hand_cards()

    assert hand["cards_in_hand_count"] == 2
    assert {card["name"] for card in hand["cards_in_hand"]} == {"Comet", "Asteroid"}
    assert all(isinstance(card["tags"], list) for card in hand["cards_in_hand"])
    assert all("cost" in card for card in hand["cards_in_hand"])
