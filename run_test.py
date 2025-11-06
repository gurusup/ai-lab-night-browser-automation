#!/usr/bin/env python3
"""Simple CLI to run QA automation tests."""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.mcp_server import MCPServer


async def run_custom_test(instruction: str):
    """Run a custom test from command line."""
    print("\n" + "=" * 60)
    print("MCP QA Automation - Custom Test")
    print("=" * 60)
    print(f"\nInstruction: {instruction}")
    print()

    async with MCPServer(use_browser_use=True, headless=False) as server:
        result = await server.execute_test(instruction)

        print("\n" + "=" * 60)
        print("Test Results")
        print("=" * 60)
        print(f"Status: {result.status.upper()}")
        print(f"Passed: {'YES' if result.passed else 'NO'}")
        print(f"Duration: {result.duration_ms}ms")

        print(f"\nActions Executed: {len(result.actions_executed)}")
        for i, action in enumerate(result.actions_executed, 1):
            status_icon = "✓" if action.get("status") == "success" else "✗"
            print(f"  {status_icon} {i}. {action.get('action')}")

        if result.screenshots:
            print(f"\nScreenshots: {len(result.screenshots)}")
            for screenshot in result.screenshots:
                print(f"  - {screenshot}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  ✗ {error}")

        print()


async def interactive_mode():
    """Run tests in interactive mode."""
    print("\n" + "=" * 60)
    print("MCP QA Automation - Interactive Mode")
    print("=" * 60)
    print("\nEnter your test instructions in natural language.")
    print("Type 'exit' or 'quit' to stop.\n")

    async with MCPServer(use_browser_use=True, headless=False) as server:
        while True:
            try:
                instruction = input("\n> Enter test instruction: ").strip()

                if instruction.lower() in ["exit", "quit", "q"]:
                    print("\nGoodbye!")
                    break

                if not instruction:
                    print("Please enter a test instruction.")
                    continue

                print("\nExecuting test...")
                result = await server.execute_test(instruction)

                print(f"\n{'=' * 40}")
                print(f"Status: {result.status} | Duration: {result.duration_ms}ms")
                print(f"{'=' * 40}")

                for i, action in enumerate(result.actions_executed, 1):
                    status = "✓" if action.get("status") == "success" else "✗"
                    print(f"{status} {i}. {action.get('action')}")

                if result.errors:
                    print("\nErrors:")
                    for error in result.errors:
                        print(f"  ✗ {error}")

            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Run with command line argument
        instruction = " ".join(sys.argv[1:])
        asyncio.run(run_custom_test(instruction))
    else:
        # Run in interactive mode
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()
