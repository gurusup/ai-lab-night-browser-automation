"""Browser automation using browser-use Agent with adaptive intelligence."""

from typing import Any, Optional, List, Dict
from pathlib import Path

from browser_use import Agent, Browser, ChatBrowserUse

from ..utils.logger import get_logger
from ..utils.config import config


logger = get_logger(__name__)


class BrowserAgent:
    """Intelligent browser automation using browser-use Agent."""

    def __init__(self, headless: Optional[bool] = None):
        """
        Initialize browser agent.

        Args:
            headless: Whether to run browser in headless mode. Defaults to config value.
        """
        self.headless = headless if headless is not None else config.headless_mode
        self.browser: Optional[Browser] = None
        self.llm = None
        logger.info("Browser Agent initialized", headless=self.headless)

    async def start(self) -> None:
        """Start the browser and LLM."""
        try:
            logger.info("Starting Browser Agent")

            # Initialize Browser
            self.browser = Browser(
                headless=self.headless,
                disable_security=False,
            )

            # Initialize LLM for Agent
            self.llm = ChatBrowserUse()

            logger.info("Browser Agent started successfully")
        except Exception as e:
            logger.error("Failed to start Browser Agent", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop the browser."""
        try:
            logger.info("Stopping Browser Agent")
            if self.browser:
                # browser-use Browser uses kill() instead of close()
                await self.browser.kill()
            logger.info("Browser Agent stopped successfully")
        except Exception as e:
            logger.error("Failed to stop Browser Agent", error=str(e))
            # Don't raise on cleanup errors
            pass

    async def execute_task(self, task: str, save_screenshot: bool = True) -> Dict[str, Any]:
        """
        Execute a task using the intelligent Agent.

        The Agent will automatically:
        - Find elements on the page
        - Adapt to DOM changes
        - Handle navigation
        - Take screenshots when needed

        Args:
            task: Natural language description of what to do
            save_screenshot: Whether to save a screenshot on successful completion

        Returns:
            Dictionary with execution results including screenshot path
        """
        if not self.browser or not self.llm:
            raise RuntimeError("Browser Agent not started. Call start() first.")

        try:
            logger.info("Executing task with Agent", task=task[:100])

            # Create Agent for this specific task
            agent = Agent(
                task=task,
                llm=self.llm,
                browser=self.browser,
            )

            # Execute the task
            history = await agent.run()

            logger.info("Task executed successfully", task=task[:50])

            # Extract result
            result = {
                "status": "success",
                "history": history,
                "message": f"Completed: {task[:100]}",
                "screenshot": None,
            }

            # Save screenshot on success
            if save_screenshot:
                try:
                    screenshot_path = await self._save_screenshot_from_history(task, history)
                    if screenshot_path:
                        result["screenshot"] = str(screenshot_path)
                        logger.info("Screenshot saved", path=str(screenshot_path))
                except Exception as screenshot_error:
                    logger.warning("Failed to save screenshot", error=str(screenshot_error))

            return result

        except Exception as e:
            logger.error("Task execution failed", task=task[:50], error=str(e))
            return {
                "status": "error",
                "error": str(e),
                "message": f"Failed: {task[:100]}",
            }

    async def _save_screenshot_from_history(self, task_description: str, history: Any) -> Optional[Path]:
        """
        Save a screenshot from Agent history or take a new one.

        The Agent automatically takes screenshots during execution. This method:
        1. First tries to get screenshots from history (base64 strings)
        2. If none exist, takes a manual screenshot of current page

        Args:
            task_description: Description to use in filename
            history: Agent history object from agent.run()

        Returns:
            Path to saved screenshot, or None if no screenshot available
        """
        import time
        import re
        import base64

        # Create a clean filename from task description
        clean_name = re.sub(r'[^\w\s-]', '', task_description[:50])
        clean_name = re.sub(r'[-\s]+', '_', clean_name).strip('_').lower()

        # Add timestamp for uniqueness
        timestamp = int(time.time())

        try:
            # First try: Check if Agent already saved screenshots to paths
            screenshot_paths = history.screenshot_paths()
            if screenshot_paths:
                # Agent saved screenshot to temp folder - copy it to our project folder
                temp_path = Path(screenshot_paths[-1])
                if temp_path.exists():
                    # Create permanent filename in project screenshots folder
                    filename = f"agent_{clean_name}_{timestamp}.png"
                    screenshot_path = config.screenshots_dir / filename

                    # Copy from temp to permanent location
                    import shutil
                    shutil.copy2(temp_path, screenshot_path)

                    logger.info("Screenshot copied from Agent temp to project",
                               source=str(temp_path), destination=str(screenshot_path))
                    return screenshot_path

        except Exception as e:
            logger.debug("No screenshot paths in history", error=str(e))

        try:
            # Second try: Get screenshots as base64 from Agent history
            screenshots = history.screenshots()

            if screenshots:
                # Use the last screenshot from the Agent's execution
                screenshot_b64 = screenshots[-1]
                filename = f"agent_{clean_name}_{timestamp}.png"
                screenshot_path = config.screenshots_dir / filename

                # Decode and save base64 screenshot
                screenshot_data = base64.b64decode(screenshot_b64)
                screenshot_path.write_bytes(screenshot_data)

                logger.info("Screenshot saved from Agent history", path=str(screenshot_path))
                return screenshot_path

        except Exception as e:
            logger.warning("Could not get screenshot from history", error=str(e))

        # Fallback: Take a manual screenshot if no history screenshots
        try:
            filename = f"agent_{clean_name}_{timestamp}_manual.png"
            screenshot_path = config.screenshots_dir / filename

            page = await self.browser.get_current_page()
            if page:
                screenshot_b64 = await page.screenshot()
                # screenshot() returns base64 string
                screenshot_data = base64.b64decode(screenshot_b64)
                screenshot_path.write_bytes(screenshot_data)

                logger.info("Manual screenshot saved", path=str(screenshot_path))
                return screenshot_path
        except Exception as e:
            logger.warning("Could not take manual screenshot", error=str(e))

        return None

    async def execute_tasks(self, tasks: List[str]) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks sequentially.

        Args:
            tasks: List of task descriptions

        Returns:
            List of results for each task
        """
        results = []

        for i, task in enumerate(tasks, 1):
            logger.info(f"Executing task {i}/{len(tasks)}", task=task[:50])
            result = await self.execute_task(task)
            results.append(result)

            # Stop on error if configured
            if result["status"] == "error":
                logger.warning("Task failed, stopping execution", task=task[:50])
                break

        return results

    async def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to

        Returns:
            Result dictionary
        """
        task = f"Navigate to {url}"
        return await self.execute_task(task)

    async def search(self, search_term: str) -> Dict[str, Any]:
        """
        Search for something on the current page.

        Args:
            search_term: What to search for

        Returns:
            Result dictionary
        """
        task = f"Find the search box on the page and search for '{search_term}'"
        return await self.execute_task(task)

    async def click(self, element_description: str) -> Dict[str, Any]:
        """
        Click an element described in natural language.

        Args:
            element_description: Description of what to click (e.g., "the blue button", "first product")

        Returns:
            Result dictionary
        """
        task = f"Click on {element_description}"
        return await self.execute_task(task)

    async def fill(self, field_description: str, text: str) -> Dict[str, Any]:
        """
        Fill a form field described in natural language.

        Args:
            field_description: Description of the field
            text: Text to enter

        Returns:
            Result dictionary
        """
        task = f"Find the {field_description} and enter '{text}'"
        return await self.execute_task(task)

    async def verify(self, expectation: str) -> Dict[str, Any]:
        """
        Verify something on the page.

        Args:
            expectation: What to verify (e.g., "the cart has items", "price is $99")

        Returns:
            Result dictionary
        """
        task = f"Verify that {expectation}"
        return await self.execute_task(task)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
