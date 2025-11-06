"""Action definitions for MCP server."""

from typing import Dict, Any, Callable, Awaitable
from enum import Enum

from ..automation.browser import BrowserAutomation
from ..automation.shopify import ShopifyActions
from ..automation.verifications import Verifications
from ..utils.logger import get_logger


logger = get_logger(__name__)


class ActionType(Enum):
    """Available action types."""

    NAVIGATE = "navigate"
    SEARCH = "search"
    CLICK = "click"
    FILL = "fill"
    ADD_TO_CART = "add_to_cart"
    GO_TO_CART = "go_to_cart"
    CHECKOUT = "checkout"
    VERIFY_TEXT = "verify_text"
    VERIFY_ELEMENT = "verify_element"
    VERIFY_URL = "verify_url"
    SCREENSHOT = "screenshot"
    SELECT_VARIANT = "select_variant"


class Action:
    """Represents a test action."""

    def __init__(
        self,
        action_type: ActionType,
        parameters: Dict[str, Any],
        description: str = "",
    ):
        """
        Initialize an action.

        Args:
            action_type: Type of action to perform
            parameters: Parameters for the action
            description: Human-readable description of the action
        """
        self.action_type = action_type
        self.parameters = parameters
        self.description = description or f"Execute {action_type.value}"

    def __repr__(self) -> str:
        """String representation of the action."""
        return f"Action({self.action_type.value}, {self.parameters})"


class ActionExecutor:
    """Executes test actions using browser automation."""

    def __init__(self, browser: BrowserAutomation):
        """
        Initialize action executor.

        Args:
            browser: BrowserAutomation instance
        """
        self.browser = browser
        self.shopify = ShopifyActions(browser)
        self.verifications = None  # Will be initialized when page is available
        logger.info("ActionExecutor initialized")

    def _get_verifications(self) -> Verifications:
        """Get or create verifications instance."""
        if self.verifications is None and self.browser.page:
            self.verifications = Verifications(self.browser.page)
        return self.verifications

    async def execute(self, action: Action) -> Dict[str, Any]:
        """
        Execute an action.

        Args:
            action: Action to execute

        Returns:
            Result dictionary with status and optional data
        """
        logger.info("Executing action", action=action.action_type.value)

        try:
            result = await self._dispatch_action(action)
            logger.info("Action executed successfully", action=action.action_type.value)
            return {"status": "success", "action": action.action_type.value, **result}
        except Exception as e:
            logger.error(
                "Action execution failed",
                action=action.action_type.value,
                error=str(e),
            )
            return {
                "status": "error",
                "action": action.action_type.value,
                "error": str(e),
            }

    async def _dispatch_action(self, action: Action) -> Dict[str, Any]:
        """
        Dispatch action to appropriate handler.

        Args:
            action: Action to dispatch

        Returns:
            Result data from the action
        """
        handlers: Dict[ActionType, Callable[[Action], Awaitable[Dict[str, Any]]]] = {
            ActionType.NAVIGATE: self._handle_navigate,
            ActionType.SEARCH: self._handle_search,
            ActionType.CLICK: self._handle_click,
            ActionType.FILL: self._handle_fill,
            ActionType.ADD_TO_CART: self._handle_add_to_cart,
            ActionType.GO_TO_CART: self._handle_go_to_cart,
            ActionType.CHECKOUT: self._handle_checkout,
            ActionType.VERIFY_TEXT: self._handle_verify_text,
            ActionType.VERIFY_ELEMENT: self._handle_verify_element,
            ActionType.VERIFY_URL: self._handle_verify_url,
            ActionType.SCREENSHOT: self._handle_screenshot,
            ActionType.SELECT_VARIANT: self._handle_select_variant,
        }

        handler = handlers.get(action.action_type)
        if not handler:
            raise ValueError(f"Unknown action type: {action.action_type}")

        return await handler(action)

    async def _handle_navigate(self, action: Action) -> Dict[str, Any]:
        """Handle navigate action."""
        url = action.parameters.get("url")
        if not url:
            raise ValueError("URL parameter required for navigate action")

        if url == "homepage":
            await self.shopify.go_to_homepage()
        else:
            await self.browser.navigate_to(url)

        return {"url": url}

    async def _handle_search(self, action: Action) -> Dict[str, Any]:
        """Handle search action."""
        search_term = action.parameters.get("term")
        if not search_term:
            raise ValueError("Term parameter required for search action")

        await self.shopify.search_product(search_term)
        return {"search_term": search_term}

    async def _handle_click(self, action: Action) -> Dict[str, Any]:
        """Handle click action."""
        selector = action.parameters.get("selector")
        if not selector:
            raise ValueError("Selector parameter required for click action")

        await self.browser.click_element(selector)
        return {"selector": selector}

    async def _handle_fill(self, action: Action) -> Dict[str, Any]:
        """Handle fill action."""
        selector = action.parameters.get("selector")
        text = action.parameters.get("text")

        if not selector or text is None:
            raise ValueError("Selector and text parameters required for fill action")

        await self.browser.fill_input(selector, text)
        return {"selector": selector}

    async def _handle_add_to_cart(self, action: Action) -> Dict[str, Any]:
        """Handle add to cart action."""
        await self.shopify.add_to_cart()
        return {}

    async def _handle_go_to_cart(self, action: Action) -> Dict[str, Any]:
        """Handle go to cart action."""
        await self.shopify.go_to_cart()
        return {}

    async def _handle_checkout(self, action: Action) -> Dict[str, Any]:
        """Handle checkout action."""
        await self.shopify.proceed_to_checkout()
        return {}

    async def _handle_verify_text(self, action: Action) -> Dict[str, Any]:
        """Handle verify text action."""
        selector = action.parameters.get("selector")
        text = action.parameters.get("text")

        if not selector or not text:
            raise ValueError("Selector and text parameters required for verify_text action")

        verifications = self._get_verifications()
        await verifications.verify_text_contains(selector, text)
        return {"selector": selector, "text": text}

    async def _handle_verify_element(self, action: Action) -> Dict[str, Any]:
        """Handle verify element action."""
        selector = action.parameters.get("selector")
        if not selector:
            raise ValueError("Selector parameter required for verify_element action")

        verifications = self._get_verifications()
        await verifications.verify_element_present(selector)
        return {"selector": selector}

    async def _handle_verify_url(self, action: Action) -> Dict[str, Any]:
        """Handle verify URL action."""
        url_part = action.parameters.get("url")
        if not url_part:
            raise ValueError("URL parameter required for verify_url action")

        verifications = self._get_verifications()
        await verifications.verify_url_contains(url_part)
        return {"url": url_part}

    async def _handle_screenshot(self, action: Action) -> Dict[str, Any]:
        """Handle screenshot action."""
        name = action.parameters.get("name", "screenshot")
        screenshot_path = await self.browser.take_screenshot(name)
        return {"screenshot_path": str(screenshot_path)}

    async def _handle_select_variant(self, action: Action) -> Dict[str, Any]:
        """Handle select variant action."""
        variant_type = action.parameters.get("type")
        variant_value = action.parameters.get("value")

        if not variant_type or not variant_value:
            raise ValueError(
                "Type and value parameters required for select_variant action"
            )

        await self.shopify.select_product_variant(variant_type, variant_value)
        return {"variant_type": variant_type, "variant_value": variant_value}
