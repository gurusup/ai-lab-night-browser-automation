"""Basic example of using the MCP server for QA automation."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server import MCPServer


async def basic_homepage_test():
    """Simple test that navigates to homepage and takes a screenshot."""
    print("=" * 60)
    print("Running Basic Homepage Test")
    print("=" * 60)

    async with MCPServer(use_browser_use=True, headless=False) as server:
        result = await server.execute_test(
            """
            Navigate to the homepage and take a screenshot
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Actions Executed: {len(result.actions_executed)}")
        print(f"Screenshots: {result.screenshots}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")


async def product_search_test():
    """Test searching for a product."""
    print("\n" + "=" * 60)
    print("Running Product Search Test")
    print("=" * 60)

    async with MCPServer(use_browser_use=True, headless=False) as server:
        result = await server.execute_test(
            """
            1. Go to the homepage
            2. Search for 'laptop'
            3. Take a screenshot of the results
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Actions Executed: {len(result.actions_executed)}")

        print("\nActions:")
        for i, action in enumerate(result.actions_executed, 1):
            print(f"  {i}. {action.get('action')} - {action.get('status')}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")


async def add_to_cart_test():
    """Test adding a product to cart."""
    print("\n" + "=" * 60)
    print("Running Add to Cart Test")
    print("=" * 60)

    async with MCPServer(use_browser_use=True, headless=False) as server:
        result = await server.execute_test(
            """
            Test the add to cart functionality:
            1. Navigate to homepage
            2. Search for 'laptop'
            3. Click on the first product
            4. Add product to cart
            5. Go to cart
            6. Take a screenshot
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Passed: {result.passed}")

        print("\nActions Executed:")
        for i, action in enumerate(result.actions_executed, 1):
            status_icon = "✓" if action.get("status") == "success" else "✗"
            print(f"  {status_icon} {i}. {action.get('action')}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")


async def main():
    """Run all example tests."""
    print("\n" + "=" * 60)
    print("MCP QA Automation - Basic Examples")
    print("=" * 60)

    try:
        # Run tests
        await basic_homepage_test()
        await product_search_test()
        await add_to_cart_test()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running tests: {e}")


if __name__ == "__main__":
    asyncio.run(main())
