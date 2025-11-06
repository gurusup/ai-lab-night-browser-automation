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
        self._setup_tools()

    def _setup_tools(self):
        """Register all available tools."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available QA automation tools."""
            return [
                Tool(
                    name="qa_automation",
                    description=(
                        "Execute browser automation tasks using natural language instructions. "
                        "The intelligent Agent will navigate websites, interact with elements, "
                        "search for products, add items to cart, fill forms, take screenshots, "
                        "and perform any web automation task you describe in plain language."
                        "\n\n"
                        "Examples:\n"
                        "- 'Search for SEVEN RUNNER METALLIC COPPER on https://thehoffbrand.com/, "
                        "add it to cart and take a screenshot'\n"
                        "- 'Go to https://example.com, find the login button, and verify it exists'\n"
                        "- 'Navigate to the homepage, search for laptop, click the first result, "
                        "and capture the product page'\n"
                        "\n"
                        "The Agent automatically:\n"
                        "- Finds elements without CSS selectors\n"
                        "- Adapts to page changes and dynamic content\n"
                        "- Takes screenshots at key moments\n"
                        "- Handles complex multi-step workflows\n"
                        "\n"
                        "Each call creates a fresh browser session for isolation."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "instruction": {
                                "type": "string",
                                "description": (
                                    "Natural language instruction describing the complete automation task. "
                                    "Be specific about URLs, product names, actions, and any verification needed. "
                                    "The Agent will execute all steps and take screenshots automatically."
                                ),
                            },
                        },
                        "required": ["instruction"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Execute a tool."""
            logger.info("Tool called", tool=name, arguments=arguments)

            try:
                if name == "qa_automation":
                    return await self._execute_automation(arguments)
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
                        text=f"Error executing automation: {str(e)}",
                    )
                ]

    async def _execute_automation(self, arguments: dict) -> list[TextContent]:
        """Execute browser automation task from natural language instruction.

        Creates a fresh agent for each call to ensure clean state.
        """
        instruction = arguments["instruction"]
        agent = None

        try:
            logger.info("Creating fresh browser agent for execution")

            # Create a new agent for this execution (ensures clean state)
            agent = BrowserAgent(headless=config.headless_mode)
            await agent.start()

            logger.info("Executing automation", instruction=instruction)

            # Execute the task with the Agent
            result = await agent.execute_task(instruction, save_screenshot=True)

            # Format response text
            response_text = f"Task: {instruction}\n\n"
            response_text += f"Status: {result['status']}\n"
            response_text += f"Result: {result['message']}\n"

            # Add error details if any
            if result.get("error"):
                response_text += f"\n\nError details: {result['error']}"

            # Build response content list
            response_content = []

            if result.get("screenshot"):
                screenshot_path = result['screenshot']
                response_text += f"\n📸 Screenshot saved at:\n{screenshot_path}\n"
                response_text += f"\n[🖼️ Click here to open screenshot](file://{screenshot_path})"

            # Return text response only (base64 images can be too large for MCP payload)
            response_content.append(TextContent(type="text", text=response_text))

            return response_content

        finally:
            # Always cleanup the agent after execution
            if agent:
                logger.info("Cleaning up browser agent")
                await agent.stop()


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
        logger.info("MCP Server shutting down")


if __name__ == "__main__":
    asyncio.run(main())
