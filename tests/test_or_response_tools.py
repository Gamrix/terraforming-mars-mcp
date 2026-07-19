from __future__ import annotations

import asyncio
import importlib
from types import SimpleNamespace
from typing import Any, cast

import terraforming_mars_mcp._tools_extra as extra_mod
import terraforming_mars_mcp.server as server_mod
import terraforming_mars_mcp.turn_flow as turn_flow
from terraforming_mars_mcp._models import PaymentPayloadModel
from terraforming_mars_mcp.api_response_models import WaitingForInputModel
from terraforming_mars_mcp.waiting_for import find_pass_option_index, prepare_action


def _wf(input_type: str) -> WaitingForInputModel:
    """Minimal real prompt model for a given input type."""
    return WaitingForInputModel.model_validate(
        {"type": input_type, "title": "", "buttonLabel": ""}
    )


def _or_menu(*titles: str) -> WaitingForInputModel:
    """An `or` prompt with one plain option per title."""
    return WaitingForInputModel.model_validate(
        {
            "type": "or",
            "title": "Take your next action",
            "buttonLabel": "OK",
            "options": [
                {"type": "option", "title": title, "buttonLabel": "OK"}
                for title in titles
            ],
        }
    )


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


_MENU = WaitingForInputModel.model_validate(_ACTION_MENU)


# --- prepare_action: the single submission-prep pipeline ---


def test_prepare_action_resolves_or_name() -> None:
    prepared = prepare_action(
        {"type": "or", "name": "End Turn", "response": {"type": "option"}}, _MENU
    )
    assert prepared == {"type": "or", "index": 1, "response": {"type": "option"}}


def test_prepare_action_resolves_templated_title_and_nested_name() -> None:
    prepared = prepare_action(
        {
            "type": "or",
            "name": "Fund an award",
            "response": {
                "type": "or",
                "name": "Banker",
                "response": {"type": "option"},
            },
        },
        _MENU,
    )
    assert prepared == {
        "type": "or",
        "index": 2,
        "response": {"type": "or", "index": 1, "response": {"type": "option"}},
    }


def test_prepare_action_resolves_standard_project_by_card_and_fills_payment() -> None:
    prepared = prepare_action(
        {
            "type": "or",
            "name": "Standard projects",
            "response": {
                "type": "projectCard",
                "card": "Power Plant:SP",
                "payment": {"megacredits": 11},
            },
        },
        _MENU,
    )
    assert prepared["index"] == 3
    response = cast("dict[str, Any]", prepared["response"])
    payment = response["payment"]
    assert payment["megacredits"] == 11
    assert payment["steel"] == 0
    assert payment["titanium"] == 0


def test_prepare_action_rejects_ambiguous_name() -> None:
    try:
        prepare_action(
            {"type": "or", "name": "an", "response": {"type": "option"}}, _MENU
        )
        assert False, "Expected RuntimeError for ambiguous option name"
    except RuntimeError as exc:
        assert "Cannot uniquely resolve" in str(exc)


def test_prepare_action_rejects_index_addressed_or() -> None:
    try:
        prepare_action(
            {"type": "or", "index": 1, "response": {"type": "option"}}, _MENU
        )
        assert False, "Expected ValueError for index-addressed or action"
    except ValueError as exc:
        assert "'name'" in str(exc)


def test_prepare_action_wraps_raw_project_card_into_branch_listing_it() -> None:
    prepared = prepare_action(
        {"type": "projectCard", "card": "Asteroid:SP", "payment": {"megacredits": 14}},
        _MENU,
    )
    assert prepared["type"] == "or"
    assert prepared["index"] == 3
    assert cast("dict[str, Any]", prepared["response"])["card"] == "Asteroid:SP"


def test_prepare_action_wraps_option_using_initial_idx() -> None:
    menu = WaitingForInputModel.model_validate(
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
    prepared = prepare_action({"type": "option"}, menu)
    assert prepared == {"type": "or", "index": 1, "response": {"type": "option"}}


def test_prepare_action_passes_through_on_non_or_prompt() -> None:
    prompt = WaitingForInputModel.model_validate(
        {"type": "option", "title": "Confirm", "buttonLabel": "OK"}
    )
    assert prepare_action({"type": "option"}, prompt) == {"type": "option"}
    assert prepare_action({"type": "space", "spaceId": "35"}, None) == {
        "type": "space",
        "spaceId": "35",
    }


def test_prepare_action_errors_when_no_branch_matches_type() -> None:
    menu = WaitingForInputModel.model_validate(
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
    try:
        prepare_action({"type": "projectCard", "card": "Noctis City"}, menu)
        assert False, "Expected RuntimeError for missing projectCard branch"
    except RuntimeError as exc:
        assert "projectCard" in str(exc)


# --- thin tool wrappers submit raw payloads; prep happens in turn_flow ---


def test_choose_or_option_submits_name_envelope() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}
    _set_submit_capture(server, captured)
    result = _run(
        server.choose_or_option(
            option_name="End Turn", sub_response={"type": "space", "spaceId": "35"}
        )
    )

    assert result == {"ok": True}
    assert captured == {
        "type": "or",
        "name": "End Turn",
        "response": {"type": "space", "spaceId": "35"},
    }


def test_confirm_option_submits_plain_option() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}
    _set_submit_capture(server, captured)
    result = _run(server.confirm_option())

    assert result == {"ok": True}
    assert captured == {"type": "option"}


def test_pass_turn_submits_static_pass_name() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}
    _set_submit_capture(server, captured)
    result = _run(server.pass_turn())

    assert result == {"ok": True}
    assert captured == {
        "type": "or",
        "name": "Pass for this generation",
        "response": {"type": "option"},
    }


def test_find_pass_option_index_never_matches_end_turn() -> None:
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
    assert find_pass_option_index(waiting_for) == 2

    end_turn_only = WaitingForInputModel.model_validate(
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
    assert find_pass_option_index(end_turn_only) is None


def test_pay_for_project_card_submits_project_card_payload() -> None:
    server = _reload_server()
    captured: dict[str, Any] = {}
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
            _wf("space"),
            _or_menu("First", "Second"),
            _or_menu("First", "Second"),
        ]
    )

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        return SimpleNamespace(waitingFor=next(next_waiting))

    extra._post_input = fake_post_input
    _stub_state_after_submission(extra)
    _stub_get_player(extra, _or_menu("First", "Second"))

    actions = [
        {"type": "or", "name": "First", "response": {"type": "option"}},
        {"type": "space", "spaceId": "35"},
        {"type": "or", "name": "Second", "response": {"type": "option"}},
    ]
    result = _run(extra.submit_multi_actions(actions=actions))

    assert len(calls) == 3
    assert calls[0] == {"type": "or", "index": 0, "response": {"type": "option"}}
    assert calls[1]["type"] == "space"
    assert calls[2] == {"type": "or", "index": 1, "response": {"type": "option"}}
    assert result["actions_executed"] == 3


def test_submit_multi_actions_stops_when_turn_ends_early() -> None:
    extra = _reload_extra()
    calls: list[dict[str, Any]] = []

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        calls.append(response)
        if len(calls) >= 2:
            return SimpleNamespace(waitingFor=None)
        return SimpleNamespace(waitingFor=_wf("space"))

    extra._post_input = fake_post_input
    _stub_state_after_submission(extra)
    _stub_get_player(extra, _or_menu("First", "Second"))

    actions = [
        {"type": "or", "name": "First", "response": {"type": "option"}},
        {"type": "space", "spaceId": "35"},
        {"type": "or", "name": "Second", "response": {"type": "option"}},
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
        return SimpleNamespace(waitingFor=_wf("or"))

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
            return SimpleNamespace(waitingFor=_wf("space"))
        return SimpleNamespace(waitingFor=_wf("or"))

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
        return SimpleNamespace(waitingFor=_wf("space"))

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
        return SimpleNamespace(waitingFor=_wf("or"))

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
        return SimpleNamespace(waitingFor=_wf("card"))

    extra._post_input = fake_post_input
    _stub_state_after_submission(extra)
    _stub_get_player(extra, _or_menu("First"))

    actions = [
        {"type": "or", "name": "First", "response": {"type": "option"}},
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


def test_submit_multi_actions_rejects_index_addressed_or() -> None:
    extra = _reload_extra()
    _stub_state_after_submission(extra)
    _stub_get_player(extra, _or_menu("First", "Second"))

    try:
        _run(
            extra.submit_multi_actions(
                actions=[{"type": "or", "index": 1, "response": {"type": "option"}}]
            )
        )
        assert False, "Expected ValueError for index-addressed or action"
    except ValueError as exc:
        assert "'name'" in str(exc)


def test_submit_and_return_state_returns_state_on_http_error(monkeypatch) -> None:

    def fake_post_input(response: Any, player_id: Any = None) -> Any:
        raise RuntimeError(
            "HTTP 400 POST /player/input: Not a valid SelectCardResponse"
        )

    def fake_get_player(player_id: Any = None) -> Any:
        return SimpleNamespace(waitingFor=_wf("card"))

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
        waitingFor=_wf("resource")
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
        waitingFor=_wf("resources")
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
        waitingFor=_wf("resource")
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
