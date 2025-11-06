"""MCP Server that exposes browser automation Agent as MCP tools.

This server allows any MCP client (Claude Desktop, Cursor, etc.) to use
our intelligent browser automation Agent for QA testing.
"""

import asyncio
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from ..automation.browser_agent import BrowserAgent
from ..utils.logger import get_logger
from ..utils.config import config

logger = get_logger(__name__)


class QAAutomationMCPServer:
    """MCP Server that exposes QA automation capabilities."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("qa-automation")
        self.agent: BrowserAgent | None = None
        self._setup_tools()

    def _setup_tools(self):
        """Register all available tools."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available QA automation tools."""
            return [
                Tool(
                    name="qa_execute_test",
                    description=(
                        "Execute a QA test using natural language. "
                        "The Agent will intelligently navigate, interact with elements, "
                        "and take screenshots. "
                        "Example: 'Go to https://example.com and search for laptop'"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Natural language description of the QA task",
                            },
                            "save_screenshot": {
                                "type": "boolean",
                                "description": "Whether to save a screenshot on completion",
                                "default": True,
                            },
                        },
                        "required": ["task"],
                    },
                ),
                Tool(
                    name="qa_navigate_and_screenshot",
                    description=(
                        "Navigate to a URL and take a screenshot. "
                        "Simple tool for quick visual verification."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to navigate to",
                            },
                        },
                        "required": ["url"],
                    },
                ),
                Tool(
                    name="qa_search_product",
                    description=(
                        "Search for a product on an e-commerce site. "
                        "The Agent will find the search box and perform the search."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "site_url": {
                                "type": "string",
                                "description": "E-commerce site URL",
                            },
                            "search_term": {
                                "type": "string",
                                "description": "Product to search for",
                            },
                        },
                        "required": ["site_url", "search_term"],
                    },
                ),
                Tool(
                    name="qa_verify_element",
                    description=(
                        "Verify that an element exists on a page using natural language. "
                        "Example: 'Verify that the shopping cart has items'"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to check",
                            },
                            "expectation": {
                                "type": "string",
                                "description": "What to verify (in natural language)",
                            },
                        },
                        "required": ["url", "expectation"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Execute a tool."""
            logger.info("Tool called", tool=name, arguments=arguments)

            # Initialize agent if needed
            if self.agent is None:
                self.agent = BrowserAgent(headless=config.headless_mode)
                await self.agent.start()

            try:
                if name == "qa_execute_test":
                    return await self._execute_test(arguments)
                elif name == "qa_navigate_and_screenshot":
                    return await self._navigate_and_screenshot(arguments)
                elif name == "qa_search_product":
                    return await self._search_product(arguments)
                elif name == "qa_verify_element":
                    return await self._verify_element(arguments)
                else:
                    return [
                        TextContent(
                            type="text",
                            text=f"Unknown tool: {name}",
                        )
                    ]
            except Exception as e:
                logger.error("Tool execution failed", tool=name, error=str(e))
                return [
                    TextContent(
                        type="text",
                        text=f"Error executing tool: {str(e)}",
                    )
                ]

    async def _execute_test(self, arguments: dict) -> list[TextContent]:
        """Execute a general QA test task."""
        task = arguments["task"]
        save_screenshot = arguments.get("save_screenshot", True)

        result = await self.agent.execute_task(task, save_screenshot=save_screenshot)

        response_text = f"Status: {result['status']}\n"
        response_text += f"Message: {result['message']}\n"

        if result.get("screenshot"):
            response_text += f"\nScreenshot saved: {result['screenshot']}"

        if result.get("error"):
            response_text += f"\nError: {result['error']}"

        return [TextContent(type="text", text=response_text)]

    async def _navigate_and_screenshot(self, arguments: dict) -> list[TextContent]:
        """Navigate to URL and take screenshot."""
        url = arguments["url"]
        task = f"Navigate to {url} and take a screenshot"

        result = await self.agent.execute_task(task, save_screenshot=True)

        response_text = f"Navigated to {url}\n"
        if result.get("screenshot"):
            response_text += f"Screenshot: {result['screenshot']}"

        return [TextContent(type="text", text=response_text)]

    async def _search_product(self, arguments: dict) -> list[TextContent]:
        """Search for a product."""
        site_url = arguments["site_url"]
        search_term = arguments["search_term"]

        task = f"""
        Navigate to {site_url}
        Find the search box and search for '{search_term}'
        Wait for results to load
        Take a screenshot of the results
        """

        result = await self.agent.execute_task(task, save_screenshot=True)

        response_text = f"Searched for '{search_term}' on {site_url}\n"
        response_text += f"Status: {result['status']}\n"

        if result.get("screenshot"):
            response_text += f"Screenshot: {result['screenshot']}"

        return [TextContent(type="text", text=response_text)]

    async def _verify_element(self, arguments: dict) -> list[TextContent]:
        """Verify an element exists."""
        url = arguments["url"]
        expectation = arguments["expectation"]

        task = f"""
        Navigate to {url}
        Verify that {expectation}
        Take a screenshot
        """

        result = await self.agent.execute_task(task, save_screenshot=True)

        response_text = f"Verification: {expectation}\n"
        response_text += f"Status: {result['status']}\n"

        if result.get("screenshot"):
            response_text += f"Screenshot: {result['screenshot']}"

        return [TextContent(type="text", text=response_text)]

    async def cleanup(self):
        """Cleanup resources."""
        if self.agent:
            await self.agent.stop()


async def main():
    """Run the MCP server."""
    logger.info("Starting QA Automation MCP Server")

    server_instance = QAAutomationMCPServer()

    try:
        async with stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                server_instance.server.create_initialization_options(),
            )
    finally:
        await server_instance.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
