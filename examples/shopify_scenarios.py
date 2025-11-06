"""Shopify-specific test scenarios using MCP server."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server import MCPServer


async def complete_purchase_flow():
    """Test the complete purchase flow from search to checkout."""
    print("=" * 60)
    print("Running Complete Purchase Flow Test")
    print("=" * 60)

    async with MCPServer(use_browser_use=True, headless=False) as server:
        result = await server.execute_test(
            """
            Test the complete purchase flow:
            1. Navigate to the homepage
            2. Search for 'blue t-shirt'
            3. Click on the first product
            4. Select size 'Medium'
            5. Add the product to cart
            6. Go to the cart
            7. Verify the cart contains items
            8. Take a screenshot of the cart
            9. Proceed to checkout
            10. Take a screenshot of the checkout page
            """
        )

        print(f"\n{'=' * 60}")
        print(f"Test Status: {result.status.upper()}")
        print(f"{'=' * 60}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Passed: {'YES' if result.passed else 'NO'}")

        print(f"\nActions Executed: {len(result.actions_executed)}")
        for i, action in enumerate(result.actions_executed, 1):
            status_icon = "✓" if action.get("status") == "success" else "✗"
            print(f"  {status_icon} Step {i}: {action.get('action')}")

        print(f"\nScreenshots Captured: {len(result.screenshots)}")
        for screenshot in result.screenshots:
            print(f"  - {screenshot}")

        if result.errors:
            print("\nErrors Encountered:")
            for error in result.errors:
                print(f"  ✗ {error}")

        return result


async def product_search_validation():
    """Test product search with validation."""
    print("\n" + "=" * 60)
    print("Running Product Search Validation Test")
    print("=" * 60)

    async with MCPServer(use_browser_use=True, headless=False) as server:
        result = await server.execute_test(
            """
            Validate product search functionality:
            1. Go to the homepage
            2. Search for 'laptop'
            3. Take a screenshot
            4. Verify the URL contains 'search'
            5. Verify the page contains text 'laptop'
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")

        print("\nValidations:")
        for action in result.actions_executed:
            if "verify" in action.get("action", ""):
                status = "PASSED" if action.get("status") == "success" else "FAILED"
                print(f"  - {action.get('action')}: {status}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")

        return result


async def cart_operations():
    """Test cart operations."""
    print("\n" + "=" * 60)
    print("Running Cart Operations Test")
    print("=" * 60)

    async with MCPServer(use_browser_use=True, headless=False) as server:
        result = await server.execute_test(
            """
            Test cart operations:
            1. Navigate to homepage
            2. Search for 'shoes'
            3. Click first product
            4. Add to cart
            5. Go to cart
            6. Verify cart URL contains 'cart'
            7. Take screenshot
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Actions: {len(result.actions_executed)}")
        print(f"Screenshots: {len(result.screenshots)}")

        if result.passed:
            print("\n✓ All cart operations completed successfully!")
        else:
            print("\n✗ Some cart operations failed")
            for error in result.errors:
                print(f"  - {error}")

        return result


async def multi_product_cart():
    """Test adding multiple products to cart."""
    print("\n" + "=" * 60)
    print("Running Multi-Product Cart Test")
    print("=" * 60)

    async with MCPServer(use_browser_use=True, headless=False) as server:
        result = await server.execute_test(
            """
            Add multiple products to cart:
            1. Go to homepage
            2. Search for 'laptop'
            3. Add first product to cart
            4. Go back to homepage
            5. Search for 'mouse'
            6. Add first product to cart
            7. Go to cart
            8. Take screenshot
            9. Verify cart has multiple items
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")

        print(f"\nTotal Actions: {len(result.actions_executed)}")
        success_count = sum(
            1 for a in result.actions_executed if a.get("status") == "success"
        )
        print(f"Successful: {success_count}/{len(result.actions_executed)}")

        if result.errors:
            print("\nIssues:")
            for error in result.errors:
                print(f"  - {error}")

        return result


async def checkout_form_test():
    """Test filling checkout form."""
    print("\n" + "=" * 60)
    print("Running Checkout Form Test")
    print("=" * 60)

    async with MCPServer(use_browser_use=True, headless=False) as server:
        result = await server.execute_test(
            """
            Test checkout form:
            1. Navigate to homepage
            2. Search for 'laptop'
            3. Add to cart
            4. Go to cart
            5. Proceed to checkout
            6. Take screenshot of checkout page
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")

        if result.passed:
            print("\n✓ Successfully navigated to checkout!")
        else:
            print("\n✗ Failed to reach checkout")

        for screenshot in result.screenshots:
            print(f"  Screenshot: {screenshot}")

        return result


async def main():
    """Run all Shopify test scenarios."""
    print("\n" + "=" * 60)
    print("MCP QA Automation - Shopify Test Scenarios")
    print("=" * 60)

    results = {}

    try:
        # Run all tests
        results["complete_flow"] = await complete_purchase_flow()
        results["search_validation"] = await product_search_validation()
        results["cart_ops"] = await cart_operations()
        results["multi_product"] = await multi_product_cart()
        results["checkout_form"] = await checkout_form_test()

        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)

        passed = sum(1 for r in results.values() if r.passed)
        total = len(results)

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        print("\nDetailed Results:")
        for test_name, result in results.items():
            status_icon = "✓" if result.passed else "✗"
            print(f"  {status_icon} {test_name}: {result.status} ({result.duration_ms}ms)")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n✗ Error running test suite: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
