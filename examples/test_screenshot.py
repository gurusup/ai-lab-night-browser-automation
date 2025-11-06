"""Quick test to verify screenshot functionality."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server.agent_server import AgentMCPServer


async def test_screenshot():
    """Simple test to verify screenshot saving works."""
    print("=" * 60)
    print("Testing Screenshot Functionality")
    print("=" * 60)

    async with AgentMCPServer(headless=False) as server:
        result = await server.execute_test(
            """
            Navigate to https://thehoffbrand.com
            Wait for the page to load completely
            Take a screenshot of the homepage
            """
        )

        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Tasks executed: {len(result.tasks_executed)}")

        if result.screenshots:
            print(f"\n✓ Screenshots captured: {len(result.screenshots)}")
            for screenshot in result.screenshots:
                print(f"  📸 {screenshot}")
        else:
            print("\n✗ No screenshots captured")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")


if __name__ == "__main__":
    asyncio.run(test_screenshot())
