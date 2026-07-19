from __future__ import annotations

import asyncio
import importlib
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


_ACTION_MENU = {
    "type": "or",
    "title": "Take your first action",
    "buttonLabel": "OK",
    "options": [
        {"type": "projectCard", "title": "Play project card", "buttonLabel": "OK"},
        {"type": "option", "title": "End Turn", "buttonLabel": "OK"},
        {
            "type": "or",
            "title": "Fund an award (${0} M€)",
            "buttonLabel": "OK",
            "options": [
                {"type": "option", "title": "Landlord", "buttonLabel": "OK"},
                {"type": "option", "title": "Banker", "buttonLabel": "OK"},
            ],
        },
        {
            "type": "projectCard",
            "title": "Standard projects",
            "buttonLabel": "OK",
            "cards": [{"name": "Power Plant:SP"}, {"name": "Asteroid:SP"}],
        },
        {
            "type": "option",
            "title": "Pass for this generation",
            "buttonLabel": "Pass",
            "warnings": ["pass"],
        },
    ],
}


def _stub_action_menu(server: Any) -> None:
    waiting_for = WaitingForInputModel.model_validate(_ACTION_MENU)
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)


def test_choose_or_option_resolves_name_and_defaults_nested_response() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}
    _set_submit_capture(server, captured)
    _stub_action_menu(server)
    result = _run(server.choose_or_option(option_name="End Turn"))

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 1, "response": {"type": "option"}}


def test_choose_or_option_resolves_templated_title_and_nested_name() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}
    _set_submit_capture(server, captured)
    _stub_action_menu(server)
    result = _run(
        server.choose_or_option(
            option_name="Fund an award",
            sub_response={
                "type": "or",
                "name": "Banker",
                "response": {"type": "option"},
            },
        )
    )

    assert result == {"ok": True}
    assert captured == {
        "type": "or",
        "index": 2,
        "response": {"type": "or", "index": 1, "response": {"type": "option"}},
    }


def test_choose_or_option_resolves_standard_project_by_card_and_fills_payment() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}
    _set_submit_capture(server, captured)
    _stub_action_menu(server)
    result = _run(
        server.choose_or_option(
            option_name="Standard projects",
            sub_response={
                "type": "projectCard",
                "card": "Power Plant:SP",
                "payment": {"megacredits": 11},
            },
        )
    )

    assert result == {"ok": True}
    assert captured["index"] == 3
    payment = captured["response"]["payment"]
    assert payment["megacredits"] == 11
    assert payment["steel"] == 0
    assert payment["titanium"] == 0


def test_choose_or_option_rejects_ambiguous_name() -> None:
    server = _reload_server()
    _set_submit_capture(server, captured={})
    _stub_action_menu(server)

    try:
        _run(server.choose_or_option(option_name="an"))
        assert False, "Expected RuntimeError for ambiguous option name"
    except RuntimeError as exc:
        assert "Cannot uniquely resolve" in str(exc)


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


def test_pass_turn_prefers_pass_over_earlier_end_turn() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}

    waiting_for = WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Take your next action",
            "buttonLabel": "OK",
            "options": [
                {"type": "option", "title": "End Turn", "buttonLabel": "End"},
                {"type": "projectCard", "title": "Play card", "buttonLabel": "OK"},
                {
                    "type": "option",
                    "title": "Pass for this generation",
                    "buttonLabel": "Pass",
                    "warnings": ["pass"],
                },
            ],
        }
    )
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    _set_submit_capture(server, captured)
    result = _run(server.pass_turn())

    assert result == {"ok": True}
    assert captured == {"type": "or", "index": 2, "response": {"type": "option"}}


def test_pass_turn_never_matches_end_turn() -> None:
    server = _reload_server()

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
    _set_submit_capture(server, captured={})

    try:
        _run(server.pass_turn())
        assert False, "Expected RuntimeError when only End Turn is available"
    except RuntimeError as exc:
        assert "No pass option" in str(exc)


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
            card_name="Noctis City", payment=PaymentPayloadModel(megacredits=18)
        )
    )

    assert result == {"ok": True}
    assert captured["type"] == "projectCard"
    assert captured["card"] == "Noctis City"
    assert captured["payment"]["megacredits"] == 18


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
            card_name="Noctis City", payment=PaymentPayloadModel(megacredits=18)
        )
    )

    assert result == {"ok": True}
    assert captured["type"] == "or"
    assert captured["index"] == 0
    assert captured["response"]["type"] == "projectCard"
    assert captured["response"]["card"] == "Noctis City"
    assert captured["response"]["payment"]["megacredits"] == 18


def test_pay_for_project_card_picks_branch_listing_the_card() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}

    waiting_for = WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Take your first action",
            "buttonLabel": "OK",
            "initialIdx": 0,
            "options": [
                {
                    "type": "projectCard",
                    "title": "Play project card",
                    "buttonLabel": "OK",
                    "cards": [{"name": "Noctis City"}],
                },
                {
                    "type": "projectCard",
                    "title": "Standard projects",
                    "buttonLabel": "OK",
                    "cards": [{"name": "Power Plant:SP"}, {"name": "Asteroid:SP"}],
                },
            ],
        }
    )
    server.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)
    _set_submit_capture(server, captured)
    result = _run(
        server.pay_for_project_card(
            card_name="Power Plant:SP", payment=PaymentPayloadModel(megacredits=11)
        )
    )

    assert result == {"ok": True}
    assert captured["type"] == "or"
    assert captured["index"] == 1
    assert captured["response"]["card"] == "Power Plant:SP"


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
                card_name="Noctis City", payment=PaymentPayloadModel(megacredits=18)
            )
        )
        assert False, "Expected RuntimeError for missing projectCard branch"
    except RuntimeError as exc:
        assert "projectCard" in str(exc)


# --- submit_multi_actions tests ---


def _reload_extra() -> Any:
    return importlib.reload(extra_mod)


def _stub_get_player(extra: Any, waiting_for: Any) -> None:
    extra.get_player = lambda player_id=None: SimpleNamespace(waitingFor=waiting_for)


def _stub_state_after_submission(extra: Any) -> None:
    async def fake_state(player_model: Any) -> dict[str, Any]:
        return {"ok": True}

    extra.state_after_submission = fake_state


def test_submit_multi_actions_chains_all_actions() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []
    # Sequence the prompts so the second action answers a `space` prompt
    # and the third answers an `or` prompt — matching the action types.
    next_waiting = iter(
        [
            SimpleNamespace(type="space"),
            SimpleNamespace(type="or"),
            SimpleNamespace(type="or"),
        ]
    )

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        return SimpleNamespace(waitingFor=next(next_waiting))

    extra._post_input = fake_post_input
    _stub_state_after_submission(extra)
    _stub_get_player(extra, SimpleNamespace(type="or"))

    actions = [
        {"type": "or", "index": 0, "response": {"type": "option"}},
        {"type": "space", "spaceId": "35"},
        {"type": "or", "index": 1, "response": {"type": "option"}},
    ]
    result = _run(extra.submit_multi_actions(actions=actions))

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

    extra._post_input = fake_post_input
    _stub_state_after_submission(extra)
    _stub_get_player(extra, SimpleNamespace(type="or"))

    actions = [
        {"type": "or", "index": 0, "response": {"type": "option"}},
        {"type": "space", "spaceId": "35"},
        {"type": "or", "index": 1, "response": {"type": "option"}},
    ]
    result = _run(extra.submit_multi_actions(actions=actions))

    assert len(calls) == 2
    assert result["actions_executed"] == 2


def test_submit_multi_actions_validates_input() -> None:
    extra = _reload_extra()
    _stub_get_player(extra, None)

    try:
        _run(extra.submit_multi_actions(actions=[]))
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "at least one" in str(exc).lower()

    try:
        _run(extra.submit_multi_actions(actions=[{"no_type": True}]))
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
    _stub_state_after_submission(extra)
    _stub_get_player(extra, None)

    actions = [
        {"type": "projectCard", "card": "Test Card"},
    ]
    _run(extra.submit_multi_actions(actions=actions))

    assert len(calls) == 1
    assert calls[0]["type"] == "projectCard"
    assert "payment" in calls[0]
    assert calls[0]["payment"]["megacredits"] == 0


def test_submit_multi_actions_chains_from_project_card() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        if len(calls) == 1:
            return SimpleNamespace(waitingFor=SimpleNamespace(type="space"))
        return SimpleNamespace(waitingFor=SimpleNamespace(type="or"))

    extra._post_input = fake_post_input
    _stub_state_after_submission(extra)
    _stub_get_player(extra, None)

    actions = [
        {"type": "projectCard", "card": "Noctis City", "payment": {"megacredits": 20}},
        {"type": "space", "spaceId": "35"},
    ]
    result = _run(extra.submit_multi_actions(actions=actions))

    assert len(calls) == 2
    assert calls[0]["type"] == "projectCard"
    assert calls[0]["card"] == "Noctis City"
    assert calls[0]["payment"]["megacredits"] == 20
    assert calls[1] == {"type": "space", "spaceId": "35"}
    assert result["actions_executed"] == 2


def test_submit_multi_actions_auto_wraps_raw_action_for_or_prompt() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        # After the wrapped projectCard, server opens a space prompt.
        return SimpleNamespace(waitingFor=SimpleNamespace(type="space"))

    extra._post_input = fake_post_input
    _stub_state_after_submission(extra)

    waiting_for = WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Take your first action",
            "buttonLabel": "Take action",
            "options": [
                {"type": "option", "title": "Pass", "buttonLabel": "Pass"},
                {
                    "type": "projectCard",
                    "title": "Play project card",
                    "buttonLabel": "Play card",
                },
            ],
        }
    )
    _stub_get_player(extra, waiting_for)

    actions = [
        {"type": "projectCard", "card": "Noctis City", "payment": {"megacredits": 20}},
        {"type": "space", "spaceId": "35"},
    ]
    result = _run(extra.submit_multi_actions(actions=actions))

    assert len(calls) == 2
    # The raw projectCard was wrapped in the matching outer `or` option.
    assert calls[0]["type"] == "or"
    assert calls[0]["index"] == 1
    assert calls[0]["response"]["type"] == "projectCard"
    assert calls[0]["response"]["card"] == "Noctis City"
    assert calls[0]["response"]["payment"]["megacredits"] == 20
    # Subsequent action answers a non-`or` prompt and is sent raw.
    assert calls[1] == {"type": "space", "spaceId": "35"}
    assert result["actions_executed"] == 2


def test_submit_multi_actions_resolves_or_names_against_live_prompt() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []

    first_menu = WaitingForInputModel.model_validate(_ACTION_MENU)
    # After the first action the menu re-orders: the award branch moves.
    second_menu = WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Take your next action",
            "buttonLabel": "OK",
            "options": [
                {"type": "option", "title": "End Turn", "buttonLabel": "OK"},
                {
                    "type": "option",
                    "title": "Pass for this generation",
                    "buttonLabel": "Pass",
                    "warnings": ["pass"],
                },
            ],
        }
    )

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        return SimpleNamespace(waitingFor=second_menu)

    extra._post_input = fake_post_input
    _stub_state_after_submission(extra)
    _stub_get_player(extra, first_menu)

    actions = [
        {"type": "or", "name": "End Turn", "response": {"type": "option"}},
        {
            "type": "or",
            "name": "Pass for this generation",
            "response": {"type": "option"},
        },
    ]
    result = _run(extra.submit_multi_actions(actions=actions))

    assert len(calls) == 2
    assert calls[0] == {"type": "or", "index": 1, "response": {"type": "option"}}
    # Same logical option resolves to its NEW index on the second prompt.
    assert calls[1] == {"type": "or", "index": 1, "response": {"type": "option"}}
    assert result["actions_executed"] == 2


def test_submit_multi_actions_normalizes_nested_payment_in_or_envelope() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        return SimpleNamespace(waitingFor=SimpleNamespace(type="or"))

    extra._post_input = fake_post_input
    _stub_state_after_submission(extra)
    _stub_get_player(extra, WaitingForInputModel.model_validate(_ACTION_MENU))

    actions = [
        {
            "type": "or",
            "name": "Standard projects",
            "response": {
                "type": "projectCard",
                "card": "Asteroid:SP",
                "payment": {"megacredits": 14},
            },
        },
    ]
    _run(extra.submit_multi_actions(actions=actions))

    assert len(calls) == 1
    assert calls[0]["index"] == 3
    payment = calls[0]["response"]["payment"]
    assert payment["megacredits"] == 14
    assert payment["heat"] == 0


def test_payment_model_rejects_old_camelcase_key() -> None:
    try:
        PaymentPayloadModel.model_validate({"megaCredits": 5})
        assert False, "Expected validation error for old megaCredits spelling"
    except Exception as exc:
        assert "megaCredits" in str(exc)


def test_submit_multi_actions_returns_state_on_http_error() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        if len(calls) == 2:
            raise RuntimeError(
                "HTTP 400 POST /player/input: Not a valid SelectCardResponse"
            )
        # After first action, server prompts for card selection.
        return SimpleNamespace(waitingFor=SimpleNamespace(type="card"))

    def fake_get_player(player_id: Any = None) -> Any:
        return SimpleNamespace(waitingFor=SimpleNamespace(type="card"))

    extra._post_input = fake_post_input
    extra.get_player = fake_get_player
    _stub_state_after_submission(extra)

    actions = [
        {"type": "or", "index": 0, "response": {"type": "option"}},
        {"type": "card", "cards": ["Ants"]},
        {"type": "card", "cards": ["Next"]},
    ]
    result = _run(extra.submit_multi_actions(actions=actions))

    assert len(calls) == 2
    assert result == {
        "ok": True,
        "actions_executed": 1,
        "error": {
            "message": "HTTP 400 POST /player/input: Not a valid SelectCardResponse",
            "failed_action_index": 1,
            "failed_action": {"type": "card", "cards": ["Ants"]},
        },
    }


def test_submit_multi_actions_leaves_or_action_unwrapped() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        return SimpleNamespace(waitingFor=SimpleNamespace(type="or"))

    extra._post_input = fake_post_input
    _stub_state_after_submission(extra)
    _stub_get_player(extra, SimpleNamespace(type="or"))

    actions = [
        {"type": "or", "index": 2, "response": {"type": "option"}},
    ]
    _run(extra.submit_multi_actions(actions=actions))

    assert len(calls) == 1
    assert calls[0] == {"type": "or", "index": 2, "response": {"type": "option"}}


def test_submit_and_return_state_returns_state_on_http_error(monkeypatch) -> None:
    import terraforming_mars_mcp.turn_flow as turn_flow

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        raise RuntimeError(
            "HTTP 400 POST /player/input: Not a valid SelectCardResponse"
        )

    def fake_get_player(player_id: Any = None) -> Any:
        return SimpleNamespace(waitingFor=SimpleNamespace(type="card"))

    monkeypatch.setattr(turn_flow, "_post_input", fake_post_input)
    monkeypatch.setattr(turn_flow, "get_player", fake_get_player)
    monkeypatch.setattr(
        turn_flow, "build_agent_state", lambda pm, **kw: {"state": "current"}
    )

    result = _run(turn_flow.submit_and_return_state({"type": "card", "cards": ["X"]}))

    assert result == {
        "state": "current",
        "error": "HTTP 400 POST /player/input: Not a valid SelectCardResponse",
    }


def test_select_resources_submits_single_resource_payload() -> None:
    extra = _reload_extra()
    captured: dict[str, Any] = {}

    async def _submit(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return {"ok": True}

    extra.get_player = lambda player_id=None: SimpleNamespace(
        waitingFor=SimpleNamespace(type="resource")
    )
    extra.submit_and_return_state = _submit

    result = _run(extra.select_resources(units=extra_mod.UnitsPayloadModel(steel=1)))

    assert result == {"ok": True}
    assert captured == {"type": "resource", "resource": "steel"}


def test_select_resources_submits_units_payload() -> None:
    extra = _reload_extra()
    captured: dict[str, Any] = {}

    async def _submit(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return {"ok": True}

    extra.get_player = lambda player_id=None: SimpleNamespace(
        waitingFor=SimpleNamespace(type="resources")
    )
    extra.submit_and_return_state = _submit

    result = _run(
        extra.select_resources(
            units=extra_mod.UnitsPayloadModel(megacredits=2, heat=1),
        )
    )

    assert result == {"ok": True}
    assert captured == {
        "type": "resources",
        "units": {
            "megacredits": 2,
            "steel": 0,
            "titanium": 0,
            "plants": 0,
            "energy": 0,
            "heat": 1,
        },
    }


def test_select_resources_validates_single_resource_selection() -> None:
    extra = _reload_extra()
    extra.get_player = lambda player_id=None: SimpleNamespace(
        waitingFor=SimpleNamespace(type="resource")
    )

    try:
        _run(
            extra.select_resources(
                units=extra_mod.UnitsPayloadModel(steel=1, heat=1),
            )
        )
        assert False, "Expected ValueError for ambiguous resource choice"
    except ValueError as exc:
        assert "exactly one" in str(exc).lower()
