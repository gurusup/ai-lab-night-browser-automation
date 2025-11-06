"""Natural language parser for test instructions."""

import re
from typing import List, Optional, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage

from .actions import Action, ActionType
from ..utils.logger import get_logger
from ..utils.config import config


logger = get_logger(__name__)


class NaturalLanguageParser:
    """Parses natural language test instructions into actions."""

    def __init__(self, use_browser_use: bool = True):
        """
        Initialize the parser.

        Args:
            use_browser_use: Whether to use ChatBrowserUse (recommended) or fallback to rule-based
        """
        self.llm = None

        # Try ChatBrowserUse first (optimized for browser automation)
        if use_browser_use and config.browser_use_api_key:
            try:
                from browser_use import ChatBrowserUse
                self.llm = ChatBrowserUse()
                logger.info("Using ChatBrowserUse for parsing (optimized)")
            except ImportError:
                logger.warning("browser-use not installed, falling back to alternatives")

        # Fallback to Anthropic
        if self.llm is None and config.anthropic_api_key:
            try:
                from langchain_anthropic import ChatAnthropic
                self.llm = ChatAnthropic(
                    api_key=config.anthropic_api_key,
                    model="claude-3-5-sonnet-20241022",
                    temperature=0,
                )
                logger.info("Using Anthropic Claude for parsing")
            except ImportError:
                logger.warning("langchain-anthropic not installed")

        # Fallback to OpenAI
        if self.llm is None and config.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    api_key=config.openai_api_key,
                    model="gpt-4o-mini",  # Using available model
                    temperature=0,
                )
                logger.info("Using OpenAI GPT-4o-mini for parsing")
            except ImportError:
                logger.warning("langchain-openai not installed")

        if self.llm is None:
            logger.warning("No LLM available, using rule-based parser only")
            self.llm = None

    async def parse(self, instruction: str) -> List[Action]:
        """
        Parse natural language instruction into actions.

        Args:
            instruction: Natural language test instruction

        Returns:
            List of Action objects
        """
        logger.info("Parsing instruction", instruction=instruction[:100])

        if self.llm:
            return await self._parse_with_llm(instruction)
        else:
            return self._parse_with_rules(instruction)

    async def _parse_with_llm(self, instruction: str) -> List[Action]:
        """
        Parse instruction using LLM.

        Args:
            instruction: Natural language instruction

        Returns:
            List of Action objects
        """
        system_prompt = """You are a QA test automation assistant. Convert natural language test instructions into structured actions.

Available action types:
- navigate: Navigate to a URL or homepage
- search: Search for a product
- click: Click an element (requires selector)
- fill: Fill an input field (requires selector and text)
- add_to_cart: Add product to cart
- go_to_cart: Navigate to shopping cart
- checkout: Proceed to checkout
- verify_text: Verify text is present (requires selector and text)
- verify_element: Verify element exists (requires selector)
- verify_url: Verify URL contains text (requires url part)
- screenshot: Take a screenshot
- select_variant: Select product variant (requires type and value)

Respond with a JSON array of actions. Each action should have:
{
  "action_type": "action_name",
  "parameters": {key: value},
  "description": "human readable description"
}

Examples:
Input: "Go to homepage and search for laptop"
Output: [
  {"action_type": "navigate", "parameters": {"url": "homepage"}, "description": "Navigate to homepage"},
  {"action_type": "search", "parameters": {"term": "laptop"}, "description": "Search for laptop"}
]

Input: "Add to cart and verify cart has items"
Output: [
  {"action_type": "add_to_cart", "parameters": {}, "description": "Add product to cart"},
  {"action_type": "go_to_cart", "parameters": {}, "description": "Navigate to cart"},
  {"action_type": "verify_element", "parameters": {"selector": ".cart-item"}, "description": "Verify cart contains items"}
]

Only respond with the JSON array, no other text."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=instruction),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            actions_data = self._extract_json_from_response(response.content)

            actions = []
            for action_data in actions_data:
                try:
                    action_type = ActionType(action_data["action_type"])
                    action = Action(
                        action_type=action_type,
                        parameters=action_data.get("parameters", {}),
                        description=action_data.get("description", ""),
                    )
                    actions.append(action)
                except (KeyError, ValueError) as e:
                    logger.warning("Failed to parse action", error=str(e), data=action_data)
                    continue

            logger.info("Parsed actions with LLM", count=len(actions))
            return actions

        except Exception as e:
            logger.error("LLM parsing failed, falling back to rules", error=str(e))
            return self._parse_with_rules(instruction)

    def _extract_json_from_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract JSON array from LLM response.

        Args:
            response: LLM response text

        Returns:
            Parsed JSON data
        """
        import json

        # Try to find JSON in the response
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)

        # If no JSON found, try to parse the whole response
        return json.loads(response)

    def _parse_with_rules(self, instruction: str) -> List[Action]:
        """
        Parse instruction using rule-based approach.

        Args:
            instruction: Natural language instruction

        Returns:
            List of Action objects
        """
        logger.info("Using rule-based parsing")

        instruction_lower = instruction.lower()
        actions: List[Action] = []

        # Split into sentences or steps
        steps = re.split(r'[.!?\n]|(?:\d+\.)', instruction)
        steps = [s.strip() for s in steps if s.strip()]

        for step in steps:
            step_lower = step.lower()

            # Navigate patterns
            if any(
                word in step_lower
                for word in ["go to", "navigate to", "visit", "open"]
            ):
                if "homepage" in step_lower or "home page" in step_lower:
                    actions.append(
                        Action(
                            ActionType.NAVIGATE,
                            {"url": "homepage"},
                            "Navigate to homepage",
                        )
                    )
                elif "cart" in step_lower:
                    actions.append(
                        Action(ActionType.GO_TO_CART, {}, "Navigate to cart")
                    )

            # Search patterns
            elif any(word in step_lower for word in ["search for", "search"]):
                # Extract search term
                match = re.search(r'search (?:for )?["\']?([^"\']+)["\']?', step_lower)
                if match:
                    search_term = match.group(1).strip()
                    actions.append(
                        Action(
                            ActionType.SEARCH,
                            {"term": search_term},
                            f"Search for {search_term}",
                        )
                    )

            # Add to cart patterns
            elif "add to cart" in step_lower or "add product" in step_lower:
                actions.append(Action(ActionType.ADD_TO_CART, {}, "Add product to cart"))

            # Checkout patterns
            elif any(
                word in step_lower for word in ["checkout", "proceed to checkout"]
            ):
                actions.append(
                    Action(ActionType.CHECKOUT, {}, "Proceed to checkout")
                )

            # Click patterns
            elif "click" in step_lower:
                # Try to extract what to click
                match = re.search(r'click (?:on |the )?["\']?([^"\']+)["\']?', step_lower)
                if match:
                    element = match.group(1).strip()
                    # Convert to selector (simplified)
                    selector = f'button:has-text("{element}")'
                    actions.append(
                        Action(
                            ActionType.CLICK, {"selector": selector}, f"Click {element}"
                        )
                    )

            # Select variant patterns
            elif "select" in step_lower or "choose" in step_lower:
                # Extract size, color, etc.
                match = re.search(
                    r'(?:select|choose) (?:size |color )?["\']?([^"\']+)["\']?',
                    step_lower,
                )
                if match:
                    variant_value = match.group(1).strip()
                    variant_type = "Size" if "size" in step_lower else "Option"
                    actions.append(
                        Action(
                            ActionType.SELECT_VARIANT,
                            {"type": variant_type, "value": variant_value},
                            f"Select {variant_type}: {variant_value}",
                        )
                    )

            # Verify patterns
            elif any(word in step_lower for word in ["verify", "check", "assert"]):
                if "url" in step_lower or "page" in step_lower:
                    # URL verification
                    match = re.search(r'contains? ["\']?([^"\']+)["\']?', step_lower)
                    if match:
                        url_part = match.group(1).strip()
                        actions.append(
                            Action(
                                ActionType.VERIFY_URL,
                                {"url": url_part},
                                f"Verify URL contains {url_part}",
                            )
                        )
                elif "text" in step_lower or "contains" in step_lower:
                    # Text verification (simplified)
                    match = re.search(r'["\']([^"\']+)["\']', step)
                    if match:
                        text = match.group(1)
                        actions.append(
                            Action(
                                ActionType.VERIFY_TEXT,
                                {"selector": "body", "text": text},
                                f"Verify text: {text}",
                            )
                        )

            # Screenshot patterns
            elif "screenshot" in step_lower or "capture" in step_lower:
                actions.append(Action(ActionType.SCREENSHOT, {}, "Take screenshot"))

        logger.info("Parsed actions with rules", count=len(actions))
        return actions
