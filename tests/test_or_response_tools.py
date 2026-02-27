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


def test_choose_or_option_defaults_nested_option_response() -> None:
    server = _load_server_module()
    captured: dict[str, Any] = {}

    def _fake_submit(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return {"ok": True}

    server._submit_and_return_state = _fake_submit

    result = server.choose_or_option(option_index=2)

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 2, "response": {"type": "option"}}


def test_choose_or_option_accepts_legacy_request_payload() -> None:
    server = _load_server_module()
    captured: dict[str, Any] = {}

    def _fake_submit(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return {"ok": True}

    server._submit_and_return_state = _fake_submit

    result = server.choose_or_option(request='{"option_index":4}')

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 4, "response": {"type": "option"}}


def test_confirm_option_submits_or_response_when_waiting_for_or() -> None:
    server = _load_server_module()
    captured: dict[str, Any] = {}

    server._get_player = lambda player_id=None: {
        "waitingFor": {
            "type": "or",
            "title": "Choose",
            "buttonLabel": "OK",
            "initialIdx": 1,
            "options": [
                {"type": "option", "title": "A", "buttonLabel": "OK"},
                {"type": "option", "title": "B", "buttonLabel": "OK"},
            ],
        }
    }

    def _fake_submit(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return {"ok": True}

    server._submit_and_return_state = _fake_submit

    result = server.confirm_option()

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 1, "response": {"type": "option"}}


def test_confirm_option_submits_option_for_option_prompt() -> None:
    server = _load_server_module()
    captured: dict[str, Any] = {}

    server._get_player = lambda player_id=None: {"waitingFor": {"type": "option", "title": "Confirm", "buttonLabel": "OK"}}

    def _fake_submit(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return {"ok": True}

    server._submit_and_return_state = _fake_submit

    result = server.confirm_option()

    assert result == {"ok": True}
    assert captured == {"type": "option"}


def test_pay_for_project_card_submits_direct_project_card_payload() -> None:
    server = _load_server_module()
    captured: dict[str, Any] = {}

    server._get_player = lambda player_id=None: {"waitingFor": {"type": "projectCard", "title": "Play", "buttonLabel": "OK"}}

    def _fake_submit(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return {"ok": True}

    server._submit_and_return_state = _fake_submit

    result = server.pay_for_project_card(card_name="Noctis City", mega_credits=18)

    assert result == {"ok": True}
    assert captured["type"] == "projectCard"
    assert captured["card"] == "Noctis City"
    assert captured["payment"]["megaCredits"] == 18


def test_pay_for_project_card_wraps_outer_or_menu() -> None:
    server = _load_server_module()
    captured: dict[str, Any] = {}

    server._get_player = lambda player_id=None: {
        "waitingFor": {
            "type": "or",
            "title": "Choose",
            "buttonLabel": "OK",
            "initialIdx": 0,
            "options": [
                {"type": "projectCard", "title": "Play card", "buttonLabel": "OK"},
                {"type": "option", "title": "Pass", "buttonLabel": "OK"},
            ],
        }
    }

    def _fake_submit(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return {"ok": True}

    server._submit_and_return_state = _fake_submit

    result = server.pay_for_project_card(card_name="Noctis City", mega_credits=18)

    assert result == {"ok": True}
    assert captured["type"] == "or"
    assert captured["index"] == 0
    assert captured["response"]["type"] == "projectCard"
    assert captured["response"]["card"] == "Noctis City"
    assert captured["response"]["payment"]["megaCredits"] == 18


def test_pay_for_project_card_errors_when_outer_or_has_no_project_card_branch() -> None:
    server = _load_server_module()

    server._get_player = lambda player_id=None: {
        "waitingFor": {
            "type": "or",
            "title": "Choose",
            "buttonLabel": "OK",
            "options": [
                {"type": "option", "title": "Pass", "buttonLabel": "OK"},
                {"type": "card", "title": "Select card", "buttonLabel": "OK"},
            ],
        }
    }

    server._submit_and_return_state = lambda payload: {"ok": True}

    try:
        server.pay_for_project_card(card_name="Noctis City", mega_credits=18)
        assert False, "Expected RuntimeError for missing projectCard branch"
    except RuntimeError as exc:
        assert "projectCard" in str(exc)
