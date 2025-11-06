"""Shopify-specific automation actions."""

from typing import Optional, Dict, Any

from .browser import BrowserAutomation
from ..utils.logger import get_logger
from ..utils.config import config


logger = get_logger(__name__)


class ShopifyActions:
    """Shopify-specific browser automation actions."""

    def __init__(self, browser: BrowserAutomation):
        """
        Initialize Shopify actions.

        Args:
            browser: BrowserAutomation instance to use
        """
        self.browser = browser
        self.base_url = config.shopify_store_url
        logger.info("Shopify actions initialized", store_url=self.base_url)

    async def go_to_homepage(self) -> None:
        """Navigate to the Shopify store homepage."""
        logger.info("Navigating to homepage")
        await self.browser.navigate_to(self.base_url)

    async def search_product(self, search_term: str) -> None:
        """
        Search for a product on the store.

        Args:
            search_term: Product name or keyword to search for
        """
        logger.info("Searching for product", search_term=search_term)

        # Common Shopify search selectors
        search_selectors = [
            'input[type="search"]',
            'input[name="q"]',
            'input[placeholder*="Search"]',
            '.search-input',
            '#search',
        ]

        for selector in search_selectors:
            try:
                await self.browser.fill_input(selector, search_term)
                await self.browser.page.keyboard.press("Enter")
                logger.info("Search executed", search_term=search_term)
                return
            except Exception:
                continue

        raise RuntimeError("Could not find search input on the page")

    async def add_to_cart(self, product_selector: Optional[str] = None) -> None:
        """
        Add a product to cart.

        Args:
            product_selector: Optional CSS selector for the product. If not provided,
                            will try common "Add to Cart" button selectors.
        """
        logger.info("Adding product to cart")

        # Common "Add to Cart" button selectors
        add_to_cart_selectors = [
            'button[name="add"]',
            'button[type="submit"][name="add"]',
            '.add-to-cart',
            '[data-action="add-to-cart"]',
            'button:has-text("Add to Cart")',
            'button:has-text("Add to cart")',
        ]

        for selector in add_to_cart_selectors:
            try:
                await self.browser.click_element(selector)
                logger.info("Product added to cart")
                return
            except Exception:
                continue

        raise RuntimeError("Could not find 'Add to Cart' button")

    async def go_to_cart(self) -> None:
        """Navigate to the shopping cart page."""
        logger.info("Navigating to cart")

        cart_selectors = [
            'a[href="/cart"]',
            'a[href*="cart"]',
            '.cart-link',
            '[data-action="open-cart"]',
        ]

        for selector in cart_selectors:
            try:
                await self.browser.click_element(selector)
                logger.info("Navigated to cart")
                return
            except Exception:
                continue

        # Fallback: directly navigate to /cart
        await self.browser.navigate_to(f"{self.base_url}/cart")

    async def proceed_to_checkout(self) -> None:
        """Proceed to the checkout page from cart."""
        logger.info("Proceeding to checkout")

        checkout_selectors = [
            'button[name="checkout"]',
            'a[href="/checkout"]',
            '.checkout-button',
            'button:has-text("Checkout")',
            'button:has-text("Check out")',
        ]

        for selector in checkout_selectors:
            try:
                await self.browser.click_element(selector)
                logger.info("Navigated to checkout")
                return
            except Exception:
                continue

        raise RuntimeError("Could not find checkout button")

    async def get_cart_total(self) -> str:
        """
        Get the total price from the cart.

        Returns:
            Cart total as a string
        """
        logger.info("Getting cart total")

        total_selectors = [
            '.cart__total',
            '.cart-total',
            '[data-cart-total]',
            '.total-price',
        ]

        for selector in total_selectors:
            try:
                total = await self.browser.get_text(selector)
                logger.info("Cart total retrieved", total=total)
                return total
            except Exception:
                continue

        raise RuntimeError("Could not find cart total")

    async def get_cart_item_count(self) -> int:
        """
        Get the number of items in the cart.

        Returns:
            Number of items in cart
        """
        logger.info("Getting cart item count")

        count_selectors = [
            '.cart-count',
            '[data-cart-count]',
            '.cart__item-count',
            '.cart-item-count',
        ]

        for selector in count_selectors:
            try:
                count_text = await self.browser.get_text(selector)
                count = int(count_text.strip())
                logger.info("Cart item count retrieved", count=count)
                return count
            except Exception:
                continue

        # Fallback: count cart items
        try:
            items = await self.browser.page.query_selector_all('.cart-item')
            count = len(items)
            logger.info("Cart item count retrieved (fallback)", count=count)
            return count
        except Exception as e:
            logger.error("Could not get cart item count", error=str(e))
            return 0

    async def fill_shipping_info(self, info: Dict[str, str]) -> None:
        """
        Fill shipping information form.

        Args:
            info: Dictionary with shipping info (email, first_name, last_name,
                  address, city, zip, country, etc.)
        """
        logger.info("Filling shipping information")

        field_mappings = {
            "email": ['input[name="email"]', '#email'],
            "first_name": ['input[name="firstName"]', '#firstName'],
            "last_name": ['input[name="lastName"]', '#lastName'],
            "address": ['input[name="address1"]', '#address1'],
            "city": ['input[name="city"]', '#city'],
            "zip": ['input[name="postalCode"]', '#zip'],
            "phone": ['input[name="phone"]', '#phone'],
        }

        for field_key, field_selectors in field_mappings.items():
            if field_key in info:
                for selector in field_selectors:
                    try:
                        await self.browser.fill_input(selector, info[field_key])
                        break
                    except Exception:
                        continue

        logger.info("Shipping information filled")

    async def select_product_variant(
        self, variant_type: str, variant_value: str
    ) -> None:
        """
        Select a product variant (e.g., size, color).

        Args:
            variant_type: Type of variant (e.g., "Size", "Color")
            variant_value: Value to select (e.g., "Medium", "Blue")
        """
        logger.info(
            "Selecting product variant",
            variant_type=variant_type,
            variant_value=variant_value,
        )

        # Try to find and select the variant
        variant_selectors = [
            f'select[name*="{variant_type.lower()}"]',
            f'[data-variant-{variant_type.lower()}]',
        ]

        for selector in variant_selectors:
            try:
                await self.browser.page.select_option(selector, variant_value)
                logger.info("Variant selected", variant=variant_value)
                return
            except Exception:
                continue

        # Try clicking on a button/label with the variant value
        try:
            await self.browser.click_element(f'button:has-text("{variant_value}")')
            logger.info("Variant selected via button", variant=variant_value)
        except Exception as e:
            logger.error(
                "Could not select variant",
                variant_type=variant_type,
                variant_value=variant_value,
                error=str(e),
            )
            raise
