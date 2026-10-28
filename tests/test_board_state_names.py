from __future__ import annotations

from terraforming_mars_mcp import game_state


def test_full_board_state_translates_tile_type_labels() -> None:
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
                    "spaceType": "land",
                    "bonus": [],
                    "tileType": 0,
                    "color": "red",
                },
                {
                    "id": "04",
                    "spaceType": "ocean",
                    "bonus": [],
                    "tileType": 1,
                    "color": "blue",
                },
            ],
        }
    )
    board_state = game_state.full_board_state(game_model)

    assert (
        board_state["reminder"]
        == "Read agent-prompts/no_guide/tharsis-board-shape.md for full board guide"
    )
    assert board_state["spaces"][0]["tile_type"] == "greenery"
    assert board_state["spaces"][1]["tile_type"] == "ocean"


def test_full_board_state_translates_bonus_labels() -> None:
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
                    "spaceType": "land",
                    "bonus": [1, 1, 3, 18, 999],
                },
            ],
        }
    )

    board_state = game_state.full_board_state(game_model, include_empty_spaces=True)

    assert board_state["spaces"][0]["bonus"] == [
        "steel",
        "steel",
        "draw card",
        "temperature (4 MC)",
        "999",
    ]


def test_board_summary_uses_tile_type_labels() -> None:
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
                    "spaceType": "land",
                    "bonus": [],
                    "tileType": 0,
                },
                {
                    "id": "04",
                    "spaceType": "ocean",
                    "bonus": [],
                    "tileType": 1,
                },
                {
                    "id": "05",
                    "spaceType": "land",
                    "bonus": [],
                    "tileType": 999,
                },
            ],
        }
    )
    summary = game_state.summarize_board(game_model)

    assert summary["tile_counts"] == {
        "greenery": 1,
        "ocean": 1,
        "999": 1,
    }


def test_full_board_state_reports_map_label() -> None:
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
                    "a9": "A1",
                    "spaceType": "land",
                    "bonus": [1, 1],
                    "tileType": 0,
                    "color": "red",
                },
            ],
        }
    )

    assert game_state.full_board_state(game_model)["spaces"] == [
        {
            "id": "03",
            "map_label": "A1",
            "space_type": "land",
            "bonus": ["steel", "steel"],
            "tile_type": "greenery",
            "owner_color": "red",
        }
    ]
