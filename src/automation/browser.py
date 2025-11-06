"""Browser automation core using Playwright."""

from typing import Any, Optional
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from ..utils.logger import get_logger
from ..utils.config import config


logger = get_logger(__name__)


class BrowserAutomation:
    """Core browser automation class using Playwright."""

    def __init__(self, headless: Optional[bool] = None):
        """
        Initialize browser automation.

        Args:
            headless: Whether to run browser in headless mode. Defaults to config value.
        """
        self.headless = headless if headless is not None else config.headless_mode
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        logger.info("Browser automation initialized", headless=self.headless)

    async def start(self) -> None:
        """Start the browser instance."""
        try:
            logger.info("Starting browser")
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error("Failed to start browser", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop the browser instance."""
        try:
            logger.info("Stopping browser")
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser stopped successfully")
        except Exception as e:
            logger.error("Failed to stop browser", error=str(e))
            raise

    async def navigate_to(self, url: str) -> None:
        """
        Navigate to a URL.

        Args:
            url: The URL to navigate to
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            logger.info("Navigating to URL", url=url)
            await self.page.goto(url, timeout=config.browser_timeout)
            logger.info("Navigation successful", url=url)
        except Exception as e:
            logger.error("Navigation failed", url=url, error=str(e))
            raise

    async def take_screenshot(self, name: str = "screenshot") -> Path:
        """
        Take a screenshot of the current page.

        Args:
            name: Name for the screenshot file

        Returns:
            Path to the saved screenshot
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            screenshot_path = config.screenshots_dir / f"{name}.png"
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info("Screenshot saved", path=str(screenshot_path))
            return screenshot_path
        except Exception as e:
            logger.error("Failed to take screenshot", error=str(e))
            raise

    async def click_element(self, selector: str) -> None:
        """
        Click an element on the page.

        Args:
            selector: CSS selector for the element
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            logger.info("Clicking element", selector=selector)
            await self.page.click(selector, timeout=config.browser_timeout)
            logger.info("Element clicked", selector=selector)
        except Exception as e:
            logger.error("Failed to click element", selector=selector, error=str(e))
            raise

    async def fill_input(self, selector: str, text: str) -> None:
        """
        Fill an input field with text.

        Args:
            selector: CSS selector for the input field
            text: Text to fill in
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            logger.info("Filling input", selector=selector)
            await self.page.fill(selector, text, timeout=config.browser_timeout)
            logger.info("Input filled", selector=selector)
        except Exception as e:
            logger.error("Failed to fill input", selector=selector, error=str(e))
            raise

    async def get_text(self, selector: str) -> str:
        """
        Get text content of an element.

        Args:
            selector: CSS selector for the element

        Returns:
            Text content of the element
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            logger.info("Getting text", selector=selector)
            element = await self.page.query_selector(selector)
            if not element:
                raise ValueError(f"Element not found: {selector}")

            text = await element.text_content()
            logger.info("Text retrieved", selector=selector, text=text)
            return text or ""
        except Exception as e:
            logger.error("Failed to get text", selector=selector, error=str(e))
            raise

    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        Wait for an element to appear on the page.

        Args:
            selector: CSS selector for the element
            timeout: Maximum time to wait in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        wait_timeout = timeout if timeout is not None else config.browser_timeout

        try:
            logger.info("Waiting for selector", selector=selector, timeout=wait_timeout)
            await self.page.wait_for_selector(selector, timeout=wait_timeout)
            logger.info("Selector found", selector=selector)
        except Exception as e:
            logger.error("Selector not found", selector=selector, error=str(e))
            raise

    async def execute_script(self, script: str) -> Any:
        """
        Execute JavaScript on the page.

        Args:
            script: JavaScript code to execute

        Returns:
            Result of the script execution
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            logger.info("Executing script")
            result = await self.page.evaluate(script)
            logger.info("Script executed successfully")
            return result
        except Exception as e:
            logger.error("Script execution failed", error=str(e))
            raise

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
