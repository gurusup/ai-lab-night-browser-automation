"""Basic example using browser-use Agent for intelligent automation."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server.agent_server import AgentMCPServer


async def intelligent_homepage_test():
    """Test using Agent - it finds elements automatically."""
    print("=" * 60)
    print("Intelligent Homepage Test (with Agent)")
    print("=" * 60)

    async with AgentMCPServer(headless=False) as server:
        result = await server.execute_test(
            """
            Navigate to https://thehoffbrand.com
            Take a screenshot of the homepage
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Tasks: {len(result.tasks_executed)}")

        if result.screenshots:
            print(f"\nScreenshots saved:")
            for screenshot in result.screenshots:
                print(f"  📸 {screenshot}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")


async def intelligent_search_test():
    """Agent automatically finds the search box and uses it."""
    print("\n" + "=" * 60)
    print("Intelligent Search Test (Agent finds search box)")
    print("=" * 60)

    async with AgentMCPServer(headless=False) as server:
        result = await server.execute_test(
            """
            Go to https://thehoffbrand.com
            Find the search functionality and search for 'shirt'
            Wait for search results to load
            Take a screenshot of the results
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")

        for i, task in enumerate(result.tasks_executed, 1):
            status_icon = "✓" if task.get("status") == "success" else "✗"
            print(f"  {status_icon} Task {i}: {task.get('message', 'Completed')[:60]}")

        if result.screenshots:
            print(f"\nScreenshots saved:")
            for screenshot in result.screenshots:
                print(f"  📸 {screenshot}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")


async def intelligent_product_test():
    """Agent navigates through product pages intelligently."""
    print("\n" + "=" * 60)
    print("Intelligent Product Test (Agent adapts to page)")
    print("=" * 60)

    async with AgentMCPServer(headless=False) as server:
        # Execute as separate steps for better tracking
        steps = [
            "Navigate to https://thehoffbrand.com",
            "Find and use the search to look for 'hat'",
            "Click on the first product in the results",
            "Verify you are on a product detail page",
        ]

        result = await server.execute_test_steps(steps)

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")

        print("\nSteps Executed:")
        for i, task in enumerate(result.tasks_executed, 1):
            status_icon = "✓" if task.get("status") == "success" else "✗"
            message = task.get('message', 'Completed')[:50]
            print(f"  {status_icon} Step {i}: {message}")

        if result.screenshots:
            print(f"\nScreenshots saved ({len(result.screenshots)}):")
            for screenshot in result.screenshots:
                print(f"  📸 {screenshot}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")


async def intelligent_cart_test():
    """Agent handles the complete cart flow."""
    print("\n" + "=" * 60)
    print("Intelligent Cart Test (Full Flow)")
    print("=" * 60)

    async with AgentMCPServer(headless=False) as server:
        result = await server.execute_test(
            """
            Test the shopping cart functionality:
            1. Go to https://thehoffbrand.com
            2. Search for any product
            3. Click on the first result
            4. Find and click the 'Add to Cart' button
            5. Navigate to the shopping cart
            6. Verify there is at least one item in the cart
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Passed: {'YES' if result.passed else 'NO'}")

        if result.screenshots:
            print(f"\nScreenshots saved:")
            for screenshot in result.screenshots:
                print(f"  📸 {screenshot}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")
        else:
            print("\n✓ All cart operations completed successfully!")


async def main():
    """Run all intelligent test examples."""
    print("\n" + "=" * 60)
    print("Browser-use Agent - Intelligent Automation Examples")
    print("=" * 60)
    print("\nThe Agent automatically:")
    print("  • Finds elements without selectors")
    print("  • Adapts to page changes")
    print("  • Handles dynamic content")
    print("  • Makes decisions based on page state")
    print()

    try:
        # Run tests
        await intelligent_homepage_test()
        await intelligent_search_test()
        await intelligent_product_test()
        await intelligent_cart_test()

        print("\n" + "=" * 60)
        print("All intelligent tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
