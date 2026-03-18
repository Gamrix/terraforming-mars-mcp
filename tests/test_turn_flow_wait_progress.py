from __future__ import annotations

import asyncio
import importlib
from types import SimpleNamespace

from terraforming_mars_mcp.api_response_models import GameLogEntryModel, PlayerViewModel
import terraforming_mars_mcp.game_state as game_state_mod
import terraforming_mars_mcp.turn_flow as turn_flow


def test_wait_for_turn_reports_progress_every_30_seconds(
    monkeypatch,
) -> None:
    clock = {"now": 0.0}
    progress_updates: list[tuple[float, float | None, str | None]] = []

    class FakeContext:
        async def report_progress(
            self,
            progress: float,
            total: float | None = None,
            message: str | None = None,
        ) -> None:
            progress_updates.append((progress, total, message))

    class FakeWaitingFor:
        def __init__(self, result: str) -> None:
            self.result = result

        def model_dump(self, exclude_none: bool = True) -> dict[str, str]:
            return {"result": self.result}

    this_player = SimpleNamespace(color="red", name="Me")
    opponent = SimpleNamespace(color="blue", name="Opponent")
    player_model = SimpleNamespace(
        game=SimpleNamespace(gameAge=1, undoCount=0),
        thisPlayer=this_player,
        players=[this_player, opponent],
        waitingFor=None,
    )

    monkeypatch.setattr(turn_flow.mcp, "get_context", lambda: FakeContext())
    monkeypatch.setattr(turn_flow.time, "monotonic", lambda: clock["now"])

    async def fake_sleep(seconds: float) -> None:
        clock["now"] += seconds

    monkeypatch.setattr(turn_flow.asyncio, "sleep", fake_sleep)

    def fake_waiting_for_state(game_age: int, undo_count: int) -> FakeWaitingFor:
        if clock["now"] >= 65:
            return FakeWaitingFor("GO")
        return FakeWaitingFor("WAIT")

    monkeypatch.setattr(turn_flow, "_get_waiting_for_state", fake_waiting_for_state)
    monkeypatch.setattr(turn_flow, "_get_player", lambda: player_model)
    monkeypatch.setattr(turn_flow, "_get_game_logs", lambda: [])

    refreshed, opponent_actions = asyncio.run(
        turn_flow._wait_for_turn_from_player_model(player_model, initial_logs=[])
    )

    assert refreshed is player_model
    assert opponent_actions == []
    assert [int(progress) for progress, _, _ in progress_updates] == [30, 60]
    assert all(
        total == float(turn_flow.TURN_WAIT_TIMEOUT_SECONDS)
        for _, total, _ in progress_updates
    )
    assert all(
        message is not None and "Waiting for opponent actions to complete" in message
        for _, _, message in progress_updates
    )


def test_submit_and_return_state_surfaces_between_turn_opponent_new_cards(
    monkeypatch,
) -> None:
    importlib.reload(game_state_mod)

    post_input_model = PlayerViewModel.model_validate(
        {
            "id": "player-1",
            "game": {
                "id": "game-1",
                "phase": "action",
                "generation": 4,
                "temperature": -20,
                "oxygenLevel": 6,
                "oceans": 3,
                "venusScaleLevel": 0,
                "isTerraformed": False,
                "gameAge": 100,
                "undoCount": 0,
                "passedPlayers": [],
                "spaces": [],
                "milestones": [],
                "awards": [],
            },
            "players": [
                {"name": "Alice", "color": "red", "isActive": False, "tableau": []},
                {"name": "John", "color": "blue", "isActive": True, "tableau": []},
            ],
            "thisPlayer": {"name": "Alice", "color": "red", "isActive": False},
        }
    )
    refreshed_model = PlayerViewModel.model_validate(
        {
            "id": "player-1",
            "game": {
                "id": "game-1",
                "phase": "action",
                "generation": 4,
                "temperature": -20,
                "oxygenLevel": 6,
                "oceans": 3,
                "venusScaleLevel": 0,
                "isTerraformed": False,
                "gameAge": 102,
                "undoCount": 0,
                "passedPlayers": [],
                "spaces": [],
                "milestones": [],
                "awards": [],
            },
            "players": [
                {"name": "Alice", "color": "red", "isActive": True, "tableau": []},
                {
                    "name": "John",
                    "color": "blue",
                    "isActive": False,
                    "tableau": [
                        {"name": "Trans-Neptune Probe"},
                        {"name": "Anti-Gravity Technology"},
                    ],
                },
            ],
            "thisPlayer": {"name": "Alice", "color": "red", "isActive": True},
            "waitingFor": {"type": "option", "title": "Play", "buttonLabel": "OK"},
        }
    )

    logs = [
        GameLogEntryModel.model_validate(
            {
                "timestamp": 1,
                "message": "${0} played Trans-Neptune Probe",
                "data": [{"type": 2, "value": "blue"}],
            }
        ),
        GameLogEntryModel.model_validate(
            {
                "timestamp": 2,
                "message": "${0} played Anti-Gravity Technology",
                "data": [{"type": 2, "value": "blue"}],
            }
        ),
    ]

    monkeypatch.setattr(turn_flow, "_post_input", lambda response: post_input_model)
    monkeypatch.setattr(turn_flow, "_get_game_logs", lambda: logs)

    async def fake_wait_for_turn_from_player_model(player_model, initial_logs=None):
        assert player_model == post_input_model
        assert initial_logs == logs
        return refreshed_model, [
            "John played Trans-Neptune Probe",
            "John played Anti-Gravity Technology",
        ]

    monkeypatch.setattr(
        turn_flow,
        "_wait_for_turn_from_player_model",
        fake_wait_for_turn_from_player_model,
    )

    result = asyncio.run(turn_flow._submit_and_return_state({"type": "option"}))

    assert result["opponent_actions_between_turns"] == [
        "John played Trans-Neptune Probe",
        "John played Anti-Gravity Technology",
    ]
    assert [card["card_name"] for card in result["opponent_new_cards"]] == [
        "Trans-Neptune Probe",
        "Anti-Gravity Technology",
    ]
