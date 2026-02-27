from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def _load_game_state_module() -> Any:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    module = importlib.import_module("terraforming_mars_mcp.game_state")
    return importlib.reload(module)


def test_full_board_state_translates_tile_type_labels() -> None:
    game_state = _load_game_state_module()
    game_model = game_state.ApiGameModel.model_validate(
        {
            "id": "game-1",
            "phase": "action",
            "generation": 1,
            "temperature": -30,
            "oxygenLevel": 0,
            "oceans": 0,
            "venusScaleLevel": 0,
            "isTerraformed": False,
            "spaces": [
                {
                    "id": "03",
                    "x": 0,
                    "y": 0,
                    "spaceType": "land",
                    "bonus": [],
                    "tileType": 0,
                    "color": "red",
                },
                {
                    "id": "04",
                    "x": 1,
                    "y": 0,
                    "spaceType": "ocean",
                    "bonus": [],
                    "tileType": 1,
                    "color": "blue",
                },
            ],
        }
    )
    board_state = game_state._full_board_state(game_model)

    assert board_state["spaces"][0]["tile_type"] == "greenery"
    assert board_state["spaces"][1]["tile_type"] == "ocean"


def test_board_summary_uses_tile_type_labels() -> None:
    game_state = _load_game_state_module()
    game_model = game_state.ApiGameModel.model_validate(
        {
            "id": "game-1",
            "phase": "action",
            "generation": 1,
            "temperature": -30,
            "oxygenLevel": 0,
            "oceans": 0,
            "venusScaleLevel": 0,
            "isTerraformed": False,
            "spaces": [
                {
                    "id": "03",
                    "x": 0,
                    "y": 0,
                    "spaceType": "land",
                    "bonus": [],
                    "tileType": 0,
                },
                {
                    "id": "04",
                    "x": 1,
                    "y": 0,
                    "spaceType": "ocean",
                    "bonus": [],
                    "tileType": 1,
                },
                {
                    "id": "05",
                    "x": 2,
                    "y": 0,
                    "spaceType": "land",
                    "bonus": [],
                    "tileType": 999,
                },
            ]
        }
    )
    summary = game_state._summarize_board(game_model)

    assert summary["tile_counts"] == {
        "greenery": 1,
        "ocean": 1,
        "999": 1,
    }
