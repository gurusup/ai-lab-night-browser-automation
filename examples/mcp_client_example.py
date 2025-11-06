"""Example of using the QA Automation MCP Server with mcp-use client.

This demonstrates how any MCP client can use our browser automation Agent
through the MCP protocol.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_use import MCPClient, MCPAgent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


async def test_mcp_server():
    """Test the QA Automation MCP Server using mcp-use client."""

    print("=" * 60)
    print("QA Automation MCP Server Client Example")
    print("=" * 60)

    # Create MCP client that connects to our QA automation server
    client = MCPClient.from_config_file("mcp_server_config.json")

    # Create an agent that uses our QA automation tools
    llm = ChatOpenAI(model="gpt-4o")
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=20,
    )

    try:
        # Example 1: Simple navigation and screenshot
        print("\n" + "=" * 60)
        print("Test 1: Navigate and Screenshot")
        print("=" * 60)

        result = await agent.run(
            "Use the QA automation tool to navigate to https://thehoffbrand.com "
            "and take a screenshot of the homepage"
        )
        print(f"\nResult: {result}")

        # Example 2: Product search
        print("\n" + "=" * 60)
        print("Test 2: Product Search")
        print("=" * 60)

        result = await agent.run(
            "Search for 'hat' on https://thehoffbrand.com using the QA automation tools"
        )
        print(f"\nResult: {result}")

        # Example 3: Complex QA task
        print("\n" + "=" * 60)
        print("Test 3: Complex QA Flow")
        print("=" * 60)

        result = await agent.run(
            """
            Execute a complete QA test:
            1. Navigate to https://thehoffbrand.com
            2. Search for 'shirt'
            3. Click on the first product
            4. Verify the product details page loaded
            5. Take a screenshot
            """
        )
        print(f"\nResult: {result}")

    finally:
        await client.close_all_sessions()


async def test_direct_tool_calls():
    """Test calling QA automation tools directly."""

    print("\n" + "=" * 60)
    print("Direct Tool Calls Example")
    print("=" * 60)

    client = MCPClient.from_config_file("mcp_server_config.json")

    try:
        # Get the session for our QA automation server
        session = client.get_session("qa-automation")

        # Example 1: Execute a QA test
        print("\nCalling qa_execute_test...")
        result = await session.call_tool(
            name="qa_execute_test",
            arguments={
                "task": "Navigate to https://thehoffbrand.com and take a screenshot",
                "save_screenshot": True,
            },
        )
        print(f"Result: {result.content[0].text}")

        # Example 2: Navigate and screenshot
        print("\nCalling qa_navigate_and_screenshot...")
        result = await session.call_tool(
            name="qa_navigate_and_screenshot",
            arguments={"url": "https://thehoffbrand.com"},
        )
        print(f"Result: {result.content[0].text}")

        # Example 3: Search product
        print("\nCalling qa_search_product...")
        result = await session.call_tool(
            name="qa_search_product",
            arguments={
                "site_url": "https://thehoffbrand.com",
                "search_term": "laptop",
            },
        )
        print(f"Result: {result.content[0].text}")

    finally:
        await client.close_all_sessions()


async def main():
    """Run all examples."""
    print("\n🤖 QA Automation MCP Server Examples")
    print("=" * 60)

    # Test with agent (high-level)
    await test_mcp_server()

    # Test with direct tool calls (low-level)
    await test_direct_tool_calls()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
