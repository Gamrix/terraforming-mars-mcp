from __future__ import annotations

import asyncio
import importlib
import json
from types import SimpleNamespace
from typing import Any

import terraforming_mars_mcp._tools_extra as extra_mod
import terraforming_mars_mcp.server as server_mod
from terraforming_mars_mcp._models import PaymentPayloadModel
from terraforming_mars_mcp.api_response_models import WaitingForInputModel


def _reload_server() -> Any:
    return importlib.reload(server_mod)


def _run(coro):
    return asyncio.run(coro)


def _set_submit_capture(
    server, captured: dict[str, Any], result: dict[str, Any] | None = None
) -> None:
    response = {"ok": True} if result is None else result

    async def _submit(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return response

    server.submit_and_return_state = _submit


def test_choose_or_option_defaults_nested_option_response() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}
    _set_submit_capture(server, captured)
    result = _run(server.choose_or_option(option_index=2))

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 2, "response": {"type": "option"}}


def test_choose_or_option_with_sub_response() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}
    _set_submit_capture(server, captured)
    result = _run(
        server.choose_or_option(
            option_index=4, sub_response={"type": "space", "spaceId": "E5"}
        )
    )

    assert result == {"ok": True}
    assert captured == {
        "type": "or",
        "index": 4,
        "response": {"type": "space", "spaceId": "E5"},
    }


def test_confirm_option_submits_or_response_when_waiting_for_or() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}

    waiting_for = WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Choose",
            "buttonLabel": "OK",
            "initialIdx": 1,
            "options": [
                {"type": "option", "title": "A", "buttonLabel": "OK"},
                {"type": "option", "title": "B", "buttonLabel": "OK"},
            ],
        }
    )
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    _set_submit_capture(server, captured)
    result = _run(server.confirm_option())

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 1, "response": {"type": "option"}}


def test_confirm_option_submits_option_for_option_prompt() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}

    waiting_for = WaitingForInputModel.model_validate(
        {"type": "option", "title": "Confirm", "buttonLabel": "OK"}
    )
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    _set_submit_capture(server, captured)
    result = _run(server.confirm_option())

    assert result == {"ok": True}
    assert captured == {"type": "option"}


def test_pass_turn_finds_pass_option_by_warning() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}

    waiting_for = WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Take your first action",
            "buttonLabel": "OK",
            "options": [
                {"type": "projectCard", "title": "Play card", "buttonLabel": "OK"},
                {"type": "card", "title": "Standard projects", "buttonLabel": "OK"},
                {
                    "type": "option",
                    "title": "Pass for this generation",
                    "buttonLabel": "Pass",
                    "warnings": ["pass"],
                },
                {"type": "card", "title": "Sell patents", "buttonLabel": "OK"},
            ],
        }
    )
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    _set_submit_capture(server, captured)
    result = _run(server.pass_turn())

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 2, "response": {"type": "option"}}


def test_pass_turn_finds_end_turn_option() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}

    waiting_for = WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Take your next action",
            "buttonLabel": "OK",
            "options": [
                {"type": "projectCard", "title": "Play card", "buttonLabel": "OK"},
                {"type": "option", "title": "End Turn", "buttonLabel": "End"},
            ],
        }
    )
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    _set_submit_capture(server, captured)
    result = _run(server.pass_turn())

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 1, "response": {"type": "option"}}


def test_pass_turn_errors_when_no_pass_option() -> None:
    server = _reload_server()

    waiting_for = WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Choose",
            "buttonLabel": "OK",
            "options": [
                {"type": "projectCard", "title": "Play card", "buttonLabel": "OK"},
                {"type": "card", "title": "Select card", "buttonLabel": "OK"},
            ],
        }
    )
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    _set_submit_capture(server, captured={})

    try:
        _run(server.pass_turn())
        assert False, "Expected RuntimeError for missing pass option"
    except RuntimeError as exc:
        assert "pass" in str(exc).lower() or "end-turn" in str(exc).lower()


def test_pay_for_project_card_submits_direct_project_card_payload() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}

    waiting_for = WaitingForInputModel.model_validate(
        {"type": "projectCard", "title": "Play", "buttonLabel": "OK"}
    )
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    _set_submit_capture(server, captured)
    result = _run(
        server.pay_for_project_card(
            card_name="Noctis City", payment=PaymentPayloadModel(megaCredits=18)
        )
    )

    assert result == {"ok": True}
    assert captured["type"] == "projectCard"
    assert captured["card"] == "Noctis City"
    assert captured["payment"]["megaCredits"] == 18


def test_pay_for_project_card_wraps_outer_or_menu() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}

    waiting_for = WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Choose",
            "buttonLabel": "OK",
            "initialIdx": 0,
            "options": [
                {"type": "projectCard", "title": "Play card", "buttonLabel": "OK"},
                {"type": "option", "title": "Pass", "buttonLabel": "OK"},
            ],
        }
    )
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    _set_submit_capture(server, captured)
    result = _run(
        server.pay_for_project_card(
            card_name="Noctis City", payment=PaymentPayloadModel(megaCredits=18)
        )
    )

    assert result == {"ok": True}
    assert captured["type"] == "or"
    assert captured["index"] == 0
    assert captured["response"]["type"] == "projectCard"
    assert captured["response"]["card"] == "Noctis City"
    assert captured["response"]["payment"]["megaCredits"] == 18


def test_pay_for_project_card_errors_when_outer_or_has_no_project_card_branch() -> None:
    server = _reload_server()

    waiting_for = WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Choose",
            "buttonLabel": "OK",
            "options": [
                {"type": "option", "title": "Pass", "buttonLabel": "OK"},
                {"type": "card", "title": "Select card", "buttonLabel": "OK"},
            ],
        }
    )
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)

    _set_submit_capture(server, captured={})

    try:
        _run(
            server.pay_for_project_card(
                card_name="Noctis City", payment=PaymentPayloadModel(megaCredits=18)
            )
        )
        assert False, "Expected RuntimeError for missing projectCard branch"
    except RuntimeError as exc:
        assert "projectCard" in str(exc)


# --- submit_multi_actions tests ---


def _reload_extra() -> Any:
    return importlib.reload(extra_mod)


def test_submit_multi_actions_chains_all_actions() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        return SimpleNamespace(waitingFor=SimpleNamespace(type="or"))

    extra._post_input = fake_post_input
    extra.build_agent_state = lambda pm, **kw: {"ok": True}

    actions = [
        {"type": "or", "index": 0, "response": {"type": "option"}},
        {"type": "space", "spaceId": "35"},
        {"type": "or", "index": 1, "response": {"type": "option"}},
    ]
    result = _run(extra.submit_multi_actions(actions_json=json.dumps(actions)))

    assert len(calls) == 3
    assert calls[0]["type"] == "or"
    assert calls[1]["type"] == "space"
    assert calls[2]["type"] == "or"
    assert result["actions_executed"] == 3


def test_submit_multi_actions_stops_when_turn_ends_early() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        if len(calls) >= 2:
            return SimpleNamespace(waitingFor=None)
        return SimpleNamespace(waitingFor=SimpleNamespace(type="space"))

    async def fake_wait(pm: Any, initial_logs: Any = None) -> Any:
        return pm, []

    extra._post_input = fake_post_input
    extra._get_game_logs = lambda player_id=None: []
    extra.wait_for_turn_from_player_model = fake_wait
    extra.build_agent_state = lambda pm, **kw: {"ok": True}

    actions = [
        {"type": "or", "index": 0, "response": {"type": "option"}},
        {"type": "space", "spaceId": "35"},
        {"type": "or", "index": 1, "response": {"type": "option"}},
    ]
    result = _run(extra.submit_multi_actions(actions_json=json.dumps(actions)))

    assert len(calls) == 2
    assert result["actions_executed"] == 2


def test_submit_multi_actions_validates_input() -> None:
    extra = _reload_extra()

    try:
        _run(extra.submit_multi_actions(actions_json='"not a list"'))
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "array" in str(exc).lower()

    try:
        _run(extra.submit_multi_actions(actions_json="[]"))
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "at least one" in str(exc).lower()

    try:
        _run(extra.submit_multi_actions(actions_json='[{"no_type": true}]'))
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "type" in str(exc).lower()


def test_submit_multi_actions_normalizes_payment() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        return SimpleNamespace(waitingFor=SimpleNamespace(type="or"))

    extra._post_input = fake_post_input
    extra.build_agent_state = lambda pm, **kw: {"ok": True}

    actions = [
        {"type": "projectCard", "card": "Test Card"},
    ]
    _run(extra.submit_multi_actions(actions_json=json.dumps(actions)))

    assert len(calls) == 1
    assert "payment" in calls[0]
    assert calls[0]["payment"]["megaCredits"] == 0
