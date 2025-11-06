"""MCP Server for natural language QA automation."""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..automation.browser import BrowserAutomation
from .parser import NaturalLanguageParser
from .actions import ActionExecutor, Action
from ..utils.logger import get_logger
from ..utils.config import config


logger = get_logger(__name__)


class TestResult:
    """Represents the result of a test execution."""

    def __init__(self):
        """Initialize test result."""
        self.status: str = "pending"
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.actions_executed: List[Dict[str, Any]] = []
        self.screenshots: List[str] = []
        self.errors: List[str] = []

    @property
    def duration_ms(self) -> Optional[int]:
        """Get test duration in milliseconds."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() * 1000)
        return None

    @property
    def passed(self) -> bool:
        """Check if test passed."""
        return self.status == "passed" and len(self.errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "passed": self.passed,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "actions_executed": self.actions_executed,
            "screenshots": self.screenshots,
            "errors": self.errors,
        }


class MCPServer:
    """MCP Server for executing natural language QA tests."""

    def __init__(self, use_browser_use: bool = True, headless: bool = False):
        """
        Initialize MCP server.

        Args:
            use_browser_use: Whether to use ChatBrowserUse (optimized, recommended)
            headless: Whether to run browser in headless mode
        """
        self.parser = NaturalLanguageParser(use_browser_use=use_browser_use)
        self.browser: Optional[BrowserAutomation] = None
        self.executor: Optional[ActionExecutor] = None
        self.headless = headless
        logger.info(
            "MCP Server initialized",
            use_browser_use=use_browser_use,
            headless=headless,
        )

    async def start(self) -> None:
        """Start the MCP server and browser."""
        logger.info("Starting MCP server")

        try:
            self.browser = BrowserAutomation(headless=self.headless)
            await self.browser.start()
            self.executor = ActionExecutor(self.browser)
            logger.info("MCP server started successfully")
        except Exception as e:
            logger.error("Failed to start MCP server", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop the MCP server and browser."""
        logger.info("Stopping MCP server")

        try:
            if self.browser:
                await self.browser.stop()
            logger.info("MCP server stopped successfully")
        except Exception as e:
            logger.error("Failed to stop MCP server", error=str(e))
            raise

    async def execute_test(self, instruction: str) -> TestResult:
        """
        Execute a test from natural language instruction.

        Args:
            instruction: Natural language test instruction

        Returns:
            TestResult object with execution details
        """
        logger.info("Executing test", instruction=instruction[:100])

        result = TestResult()
        result.start_time = datetime.now()
        result.status = "running"

        try:
            # Parse instruction into actions
            actions = await self.parser.parse(instruction)
            logger.info("Parsed actions", count=len(actions))

            if not actions:
                result.status = "failed"
                result.errors.append("No actions could be parsed from instruction")
                result.end_time = datetime.now()
                return result

            # Execute each action
            for i, action in enumerate(actions):
                logger.info(
                    "Executing action",
                    index=i + 1,
                    total=len(actions),
                    action=action.description,
                )

                action_result = await self.executor.execute(action)
                result.actions_executed.append(action_result)

                # Collect screenshots
                if "screenshot_path" in action_result:
                    result.screenshots.append(action_result["screenshot_path"])

                # Handle errors
                if action_result["status"] == "error":
                    error_msg = f"Action failed: {action.description} - {action_result.get('error', 'Unknown error')}"
                    result.errors.append(error_msg)
                    logger.error("Action failed", action=action.description)

                    # Take error screenshot
                    try:
                        screenshot_path = await self.browser.take_screenshot(
                            f"error_step_{i + 1}"
                        )
                        result.screenshots.append(str(screenshot_path))
                    except Exception:
                        pass

                    # Stop on error
                    break

            # Determine final status
            if result.errors:
                result.status = "failed"
            else:
                result.status = "passed"

            result.end_time = datetime.now()

            logger.info(
                "Test execution completed",
                status=result.status,
                duration_ms=result.duration_ms,
            )

            return result

        except Exception as e:
            logger.error("Test execution error", error=str(e))
            result.status = "error"
            result.errors.append(f"Test execution error: {str(e)}")
            result.end_time = datetime.now()
            return result

    async def execute_actions(self, actions: List[Action]) -> TestResult:
        """
        Execute a list of actions directly.

        Args:
            actions: List of Action objects to execute

        Returns:
            TestResult object with execution details
        """
        logger.info("Executing actions", count=len(actions))

        result = TestResult()
        result.start_time = datetime.now()
        result.status = "running"

        try:
            for i, action in enumerate(actions):
                logger.info(
                    "Executing action",
                    index=i + 1,
                    total=len(actions),
                    action=action.description,
                )

                action_result = await self.executor.execute(action)
                result.actions_executed.append(action_result)

                if "screenshot_path" in action_result:
                    result.screenshots.append(action_result["screenshot_path"])

                if action_result["status"] == "error":
                    error_msg = f"Action failed: {action.description} - {action_result.get('error', 'Unknown error')}"
                    result.errors.append(error_msg)

                    try:
                        screenshot_path = await self.browser.take_screenshot(
                            f"error_step_{i + 1}"
                        )
                        result.screenshots.append(str(screenshot_path))
                    except Exception:
                        pass

                    break

            result.status = "passed" if not result.errors else "failed"
            result.end_time = datetime.now()

            return result

        except Exception as e:
            logger.error("Actions execution error", error=str(e))
            result.status = "error"
            result.errors.append(f"Execution error: {str(e)}")
            result.end_time = datetime.now()
            return result

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


# Example usage
async def main():
    """Example main function."""
    # Create and start server (uses ChatBrowserUse by default)
    async with MCPServer(use_browser_use=True, headless=False) as server:
        # Execute a test
        result = await server.execute_test(
            """
            Test the product search functionality:
            1. Go to the homepage
            2. Search for 'laptop'
            3. Take a screenshot
            """
        )

        # Print results
        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Actions Executed: {len(result.actions_executed)}")
        print(f"Screenshots: {len(result.screenshots)}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")


if __name__ == "__main__":
    asyncio.run(main())
