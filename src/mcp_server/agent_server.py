"""MCP Server using browser-use Agent for intelligent automation."""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..automation.browser_agent import BrowserAgent
from ..utils.logger import get_logger
from ..utils.config import config


logger = get_logger(__name__)


class AgentTestResult:
    """Represents the result of a test execution using Agent."""

    def __init__(self):
        """Initialize test result."""
        self.status: str = "pending"
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.tasks_executed: List[Dict[str, Any]] = []
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
            "tasks_executed": self.tasks_executed,
            "screenshots": self.screenshots,
            "errors": self.errors,
        }


class AgentMCPServer:
    """MCP Server using browser-use Agent for intelligent test automation."""

    def __init__(self, headless: bool = False):
        """
        Initialize Agent MCP server.

        Args:
            headless: Whether to run browser in headless mode
        """
        self.agent: Optional[BrowserAgent] = None
        self.headless = headless
        logger.info(
            "Agent MCP Server initialized",
            headless=headless,
        )

    async def start(self) -> None:
        """Start the MCP server and browser agent."""
        logger.info("Starting Agent MCP server")

        try:
            self.agent = BrowserAgent(headless=self.headless)
            await self.agent.start()
            logger.info("Agent MCP server started successfully")
        except Exception as e:
            logger.error("Failed to start Agent MCP server", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop the MCP server and browser agent."""
        logger.info("Stopping Agent MCP server")

        try:
            if self.agent:
                await self.agent.stop()
            logger.info("Agent MCP server stopped successfully")
        except Exception as e:
            logger.error("Failed to stop Agent MCP server", error=str(e))
            raise

    async def execute_test(self, instruction: str) -> AgentTestResult:
        """
        Execute a test from natural language instruction.

        The Agent will intelligently:
        - Parse the instruction
        - Find elements automatically
        - Adapt to page changes
        - Handle errors gracefully

        Args:
            instruction: Natural language test instruction

        Returns:
            AgentTestResult object with execution details
        """
        logger.info("Executing test with Agent", instruction=instruction[:100])

        result = AgentTestResult()
        result.start_time = datetime.now()
        result.status = "running"

        try:
            # The Agent handles everything - just pass the full instruction
            task_result = await self.agent.execute_task(instruction)
            result.tasks_executed.append(task_result)

            # Collect screenshot if available
            if task_result.get("screenshot"):
                result.screenshots.append(task_result["screenshot"])

            # Check for errors
            if task_result["status"] == "error":
                result.errors.append(task_result.get("error", "Unknown error"))
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

    async def execute_test_steps(self, steps: List[str]) -> AgentTestResult:
        """
        Execute a test with multiple steps.

        Each step is executed by the Agent independently, allowing for
        better error tracking and reporting.

        Args:
            steps: List of test steps in natural language

        Returns:
            AgentTestResult object with execution details
        """
        logger.info("Executing test steps with Agent", count=len(steps))

        result = AgentTestResult()
        result.start_time = datetime.now()
        result.status = "running"

        try:
            # Execute each step
            for i, step in enumerate(steps, 1):
                logger.info(f"Executing step {i}/{len(steps)}", step=step[:50])

                task_result = await self.agent.execute_task(step)
                result.tasks_executed.append(task_result)

                # Collect screenshot if available
                if task_result.get("screenshot"):
                    result.screenshots.append(task_result["screenshot"])

                # Check for errors
                if task_result["status"] == "error":
                    error_msg = f"Step {i} failed: {task_result.get('error', 'Unknown error')}"
                    result.errors.append(error_msg)
                    logger.error("Step failed", step=step[:50])
                    break

            # Determine final status
            result.status = "passed" if not result.errors else "failed"
            result.end_time = datetime.now()

            logger.info(
                "Test steps completed",
                status=result.status,
                duration_ms=result.duration_ms,
            )

            return result

        except Exception as e:
            logger.error("Test steps execution error", error=str(e))
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
    # Create and start server (uses browser-use Agent)
    async with AgentMCPServer(headless=False) as server:
        # Execute a test - Agent finds elements automatically
        result = await server.execute_test(
            """
            Go to https://thehoffbrand.com
            Find the search box and search for 'laptop'
            Click on the first product result
            Verify the product page loaded correctly
            """
        )

        # Print results
        print(f"\nTest Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Tasks Executed: {len(result.tasks_executed)}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")


if __name__ == "__main__":
    asyncio.run(main())
