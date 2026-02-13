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
            "initialIdx": 1,
            "options": [{"type": "option"}, {"type": "option"}],
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

    server._get_player = lambda player_id=None: {"waitingFor": {"type": "option"}}

    def _fake_submit(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return {"ok": True}

    server._submit_and_return_state = _fake_submit

    result = server.confirm_option()

    assert result == {"ok": True}
    assert captured == {"type": "option"}

