from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Any

import terraforming_mars_mcp.server as server_mod
from terraforming_mars_mcp.api_response_models import WaitingForInputModel


def test_choose_or_option_defaults_nested_option_response() -> None:
    server = importlib.reload(server_mod)
    captured: dict[str, Any] = {}

    server._submit_and_return_state = lambda payload: (
        captured.update(payload) or {"ok": True}
    )

    result = server.choose_or_option(option_index=2)

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 2, "response": {"type": "option"}}


def test_choose_or_option_accepts_legacy_request_payload() -> None:
    server = importlib.reload(server_mod)
    captured: dict[str, Any] = {}

    server._submit_and_return_state = lambda payload: (
        captured.update(payload) or {"ok": True}
    )

    result = server.choose_or_option(request='{"option_index":4}')

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 4, "response": {"type": "option"}}


def test_confirm_option_submits_or_response_when_waiting_for_or() -> None:
    server = importlib.reload(server_mod)
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
    server._get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    server._submit_and_return_state = lambda payload: (
        captured.update(payload) or {"ok": True}
    )

    result = server.confirm_option()

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 1, "response": {"type": "option"}}


def test_confirm_option_submits_option_for_option_prompt() -> None:
    server = importlib.reload(server_mod)
    captured: dict[str, Any] = {}

    waiting_for = WaitingForInputModel.model_validate(
        {"type": "option", "title": "Confirm", "buttonLabel": "OK"}
    )
    server._get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    server._submit_and_return_state = lambda payload: (
        captured.update(payload) or {"ok": True}
    )

    result = server.confirm_option()

    assert result == {"ok": True}
    assert captured == {"type": "option"}


def test_pay_for_project_card_submits_direct_project_card_payload() -> None:
    server = importlib.reload(server_mod)
    captured: dict[str, Any] = {}

    waiting_for = WaitingForInputModel.model_validate(
        {"type": "projectCard", "title": "Play", "buttonLabel": "OK"}
    )
    server._get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    server._submit_and_return_state = lambda payload: (
        captured.update(payload) or {"ok": True}
    )

    result = server.pay_for_project_card(card_name="Noctis City", mega_credits=18)

    assert result == {"ok": True}
    assert captured["type"] == "projectCard"
    assert captured["card"] == "Noctis City"
    assert captured["payment"]["megaCredits"] == 18


def test_pay_for_project_card_wraps_outer_or_menu() -> None:
    server = importlib.reload(server_mod)
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
    server._get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    server._submit_and_return_state = lambda payload: (
        captured.update(payload) or {"ok": True}
    )

    result = server.pay_for_project_card(card_name="Noctis City", mega_credits=18)

    assert result == {"ok": True}
    assert captured["type"] == "or"
    assert captured["index"] == 0
    assert captured["response"]["type"] == "projectCard"
    assert captured["response"]["card"] == "Noctis City"
    assert captured["response"]["payment"]["megaCredits"] == 18


def test_pay_for_project_card_errors_when_outer_or_has_no_project_card_branch() -> None:
    server = importlib.reload(server_mod)

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
    server._get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)

    server._submit_and_return_state = lambda payload: {"ok": True}

    try:
        server.pay_for_project_card(card_name="Noctis City", mega_credits=18)
        assert False, "Expected RuntimeError for missing projectCard branch"
    except RuntimeError as exc:
        assert "projectCard" in str(exc)
