from __future__ import annotations

import logging
from typing import Any

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError, UnexpectedToolError
from mcp_types import CallToolResult, InputRequiredResult

logger = logging.getLogger(__name__)


class TerraformingMarsServer(MCPServer):
    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        context: Context[Any, Any] | None = None,
    ) -> CallToolResult | InputRequiredResult:
        # mcp 2.x hides the text of any exception that is not a ToolError. Our
        # tools raise ValueError/RuntimeError/TimeoutError with messages the
        # agent needs (bad input, rejected action, wait timeout), so pass the
        # original message through.
        try:
            return await super().call_tool(name, arguments, context)
        except UnexpectedToolError as exc:
            logger.error("Tool %s failed", name, exc_info=exc.__cause__)
            raise ToolError(f"{exc}: {exc.__cause__}") from exc.__cause__


mcp = TerraformingMarsServer("terraforming-mars", log_level="DEBUG", debug=True)
