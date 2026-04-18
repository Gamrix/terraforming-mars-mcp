from __future__ import annotations

from terraforming_mars_mcp._enums import ToolName, action_tools_for_input_type


def test_removed_input_types_fall_back_to_submit_raw_entity() -> None:
    for input_type in (
        "delegate",
        "aresGlobalParameters",
        "globalEvent",
        "policy",
        "claimedUndergroundToken",
    ):
        assert action_tools_for_input_type(input_type) == [
            ToolName.SUBMIT_RAW_ENTITY.value
        ]


def test_resource_and_resources_prompts_share_select_resources_tool() -> None:
    assert action_tools_for_input_type("resource") == [
        ToolName.SELECT_RESOURCES.value,
        ToolName.SUBMIT_RAW_ENTITY.value,
    ]
    assert action_tools_for_input_type("resources") == [
        ToolName.SELECT_RESOURCES.value,
        ToolName.SUBMIT_RAW_ENTITY.value,
    ]
