from __future__ import annotations

import asyncio
from types import SimpleNamespace

import terraforming_mars_mcp.turn_flow as turn_flow


def test_wait_for_turn_reports_progress_every_30_seconds(
    monkeypatch,
) -> None:
    clock = {"now": 0.0}
    progress_updates: list[tuple[float, float | None, str | None]] = []

    class FakeContext:
        async def report_progress(
            self, progress: float, total: float | None = None, message: str | None = None
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
    assert all(total == float(turn_flow.TURN_WAIT_TIMEOUT_SECONDS) for _, total, _ in progress_updates)
    assert all(
        message is not None and "Waiting for opponent actions to complete" in message
        for _, _, message in progress_updates
    )
