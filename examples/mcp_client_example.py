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

        # Example 3: Complex workflow - Search and add to cart
        print("\n" + "=" * 60)
        print("Test 3: Complex Workflow - Search and Add to Cart")
        print("=" * 60)

        result = await agent.run(
            """
            Use the QA automation tool to:
            Search for SEVEN RUNNER METALLIC COPPER on https://thehoffbrand.com/,
            add it to cart and generate screenshot
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

        # Example 1: Simple navigation
        print("\nTest 1: Simple Navigation")
        result = await session.call_tool(
            name="qa_automation",
            arguments={
                "instruction": "Navigate to https://thehoffbrand.com and take a screenshot"
            },
        )
        print(f"Result: {result.content[0].text}\n")

        # Example 2: Product search
        print("\nTest 2: Product Search")
        result = await session.call_tool(
            name="qa_automation",
            arguments={
                "instruction": "Go to https://thehoffbrand.com, search for 'hat', and capture the results"
            },
        )
        print(f"Result: {result.content[0].text}\n")

        # Example 3: Complex workflow (your exact use case)
        print("\nTest 3: Search Product and Add to Cart")
        result = await session.call_tool(
            name="qa_automation",
            arguments={
                "instruction": (
                    "Search for SEVEN RUNNER METALLIC COPPER on https://thehoffbrand.com/, "
                    "add it to cart and generate screenshot"
                )
            },
        )
        print(f"Result: {result.content[0].text}\n")

        # Example 4: Element verification
        print("\nTest 4: Verify Element")
        result = await session.call_tool(
            name="qa_automation",
            arguments={
                "instruction": "Go to https://thehoffbrand.com/cart and verify that the shopping cart is empty or has items"
            },
        )
        print(f"Result: {result.content[0].text}\n")

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
