"""Test assertion and verification utilities."""

from typing import Optional
from playwright.async_api import Page

from ..utils.logger import get_logger


logger = get_logger(__name__)


class VerificationError(Exception):
    """Exception raised when a verification fails."""

    pass


class Verifications:
    """Test verification and assertion utilities."""

    def __init__(self, page: Page):
        """
        Initialize verifications.

        Args:
            page: Playwright page instance
        """
        self.page = page
        logger.info("Verifications initialized")

    async def verify_element_present(self, selector: str, timeout: int = 5000) -> None:
        """
        Verify that an element is present on the page.

        Args:
            selector: CSS selector for the element
            timeout: Maximum time to wait in milliseconds

        Raises:
            VerificationError: If element is not found
        """
        logger.info("Verifying element present", selector=selector)
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            logger.info("Element verification passed", selector=selector)
        except Exception as e:
            logger.error("Element verification failed", selector=selector, error=str(e))
            raise VerificationError(f"Element not found: {selector}") from e

    async def verify_element_not_present(
        self, selector: str, timeout: int = 5000
    ) -> None:
        """
        Verify that an element is NOT present on the page.

        Args:
            selector: CSS selector for the element
            timeout: Maximum time to wait in milliseconds

        Raises:
            VerificationError: If element is found
        """
        logger.info("Verifying element not present", selector=selector)
        try:
            element = await self.page.query_selector(selector)
            if element:
                raise VerificationError(f"Element should not be present: {selector}")
            logger.info("Element not present verification passed", selector=selector)
        except VerificationError:
            raise
        except Exception as e:
            logger.error(
                "Element not present verification error",
                selector=selector,
                error=str(e),
            )
            raise

    async def verify_text_contains(
        self, selector: str, expected_text: str, case_sensitive: bool = False
    ) -> None:
        """
        Verify that an element's text contains expected text.

        Args:
            selector: CSS selector for the element
            expected_text: Text that should be present
            case_sensitive: Whether comparison should be case-sensitive

        Raises:
            VerificationError: If text is not found
        """
        logger.info(
            "Verifying text contains",
            selector=selector,
            expected_text=expected_text,
        )

        try:
            element = await self.page.query_selector(selector)
            if not element:
                raise VerificationError(f"Element not found: {selector}")

            actual_text = await element.text_content()
            if actual_text is None:
                actual_text = ""

            if not case_sensitive:
                actual_text = actual_text.lower()
                expected_text = expected_text.lower()

            if expected_text not in actual_text:
                raise VerificationError(
                    f"Text '{expected_text}' not found in element. Actual text: '{actual_text}'"
                )

            logger.info("Text contains verification passed", selector=selector)
        except VerificationError:
            raise
        except Exception as e:
            logger.error(
                "Text contains verification failed", selector=selector, error=str(e)
            )
            raise VerificationError(f"Failed to verify text in {selector}") from e

    async def verify_text_equals(
        self, selector: str, expected_text: str, case_sensitive: bool = False
    ) -> None:
        """
        Verify that an element's text equals expected text.

        Args:
            selector: CSS selector for the element
            expected_text: Exact text that should be present
            case_sensitive: Whether comparison should be case-sensitive

        Raises:
            VerificationError: If text doesn't match
        """
        logger.info(
            "Verifying text equals", selector=selector, expected_text=expected_text
        )

        try:
            element = await self.page.query_selector(selector)
            if not element:
                raise VerificationError(f"Element not found: {selector}")

            actual_text = (await element.text_content() or "").strip()

            if not case_sensitive:
                actual_text = actual_text.lower()
                expected_text = expected_text.lower()

            if actual_text != expected_text:
                raise VerificationError(
                    f"Text mismatch. Expected: '{expected_text}', Actual: '{actual_text}'"
                )

            logger.info("Text equals verification passed", selector=selector)
        except VerificationError:
            raise
        except Exception as e:
            logger.error("Text equals verification failed", selector=selector, error=str(e))
            raise VerificationError(f"Failed to verify text in {selector}") from e

    async def verify_url_contains(self, expected_url_part: str) -> None:
        """
        Verify that the current URL contains expected text.

        Args:
            expected_url_part: Text that should be in the URL

        Raises:
            VerificationError: If URL doesn't contain expected text
        """
        logger.info("Verifying URL contains", expected=expected_url_part)

        current_url = self.page.url
        if expected_url_part not in current_url:
            raise VerificationError(
                f"URL doesn't contain '{expected_url_part}'. Current URL: {current_url}"
            )

        logger.info("URL contains verification passed", url=current_url)

    async def verify_url_equals(self, expected_url: str) -> None:
        """
        Verify that the current URL equals expected URL.

        Args:
            expected_url: Exact URL that should be current

        Raises:
            VerificationError: If URL doesn't match
        """
        logger.info("Verifying URL equals", expected=expected_url)

        current_url = self.page.url
        if current_url != expected_url:
            raise VerificationError(
                f"URL mismatch. Expected: '{expected_url}', Actual: '{current_url}'"
            )

        logger.info("URL equals verification passed", url=current_url)

    async def verify_element_visible(self, selector: str, timeout: int = 5000) -> None:
        """
        Verify that an element is visible on the page.

        Args:
            selector: CSS selector for the element
            timeout: Maximum time to wait in milliseconds

        Raises:
            VerificationError: If element is not visible
        """
        logger.info("Verifying element visible", selector=selector)

        try:
            await self.page.wait_for_selector(
                selector, state="visible", timeout=timeout
            )
            logger.info("Element visible verification passed", selector=selector)
        except Exception as e:
            logger.error(
                "Element visible verification failed", selector=selector, error=str(e)
            )
            raise VerificationError(f"Element not visible: {selector}") from e

    async def verify_element_count(
        self, selector: str, expected_count: int, comparison: str = "equal"
    ) -> None:
        """
        Verify the count of elements matching a selector.

        Args:
            selector: CSS selector for the elements
            expected_count: Expected number of elements
            comparison: Comparison type: "equal", "greater", "less", "at_least", "at_most"

        Raises:
            VerificationError: If count doesn't match expectation
        """
        logger.info(
            "Verifying element count",
            selector=selector,
            expected=expected_count,
            comparison=comparison,
        )

        try:
            elements = await self.page.query_selector_all(selector)
            actual_count = len(elements)

            is_valid = False
            if comparison == "equal":
                is_valid = actual_count == expected_count
            elif comparison == "greater":
                is_valid = actual_count > expected_count
            elif comparison == "less":
                is_valid = actual_count < expected_count
            elif comparison == "at_least":
                is_valid = actual_count >= expected_count
            elif comparison == "at_most":
                is_valid = actual_count <= expected_count
            else:
                raise ValueError(f"Invalid comparison type: {comparison}")

            if not is_valid:
                raise VerificationError(
                    f"Element count verification failed. Expected {comparison} {expected_count}, "
                    f"but found {actual_count}"
                )

            logger.info(
                "Element count verification passed",
                selector=selector,
                count=actual_count,
            )
        except VerificationError:
            raise
        except Exception as e:
            logger.error(
                "Element count verification error", selector=selector, error=str(e)
            )
            raise VerificationError(f"Failed to verify element count for {selector}") from e

    async def verify_attribute(
        self, selector: str, attribute: str, expected_value: str
    ) -> None:
        """
        Verify that an element's attribute has expected value.

        Args:
            selector: CSS selector for the element
            attribute: Attribute name
            expected_value: Expected attribute value

        Raises:
            VerificationError: If attribute doesn't match
        """
        logger.info(
            "Verifying attribute",
            selector=selector,
            attribute=attribute,
            expected=expected_value,
        )

        try:
            element = await self.page.query_selector(selector)
            if not element:
                raise VerificationError(f"Element not found: {selector}")

            actual_value = await element.get_attribute(attribute)
            if actual_value != expected_value:
                raise VerificationError(
                    f"Attribute '{attribute}' mismatch. Expected: '{expected_value}', "
                    f"Actual: '{actual_value}'"
                )

            logger.info("Attribute verification passed", selector=selector)
        except VerificationError:
            raise
        except Exception as e:
            logger.error(
                "Attribute verification failed", selector=selector, error=str(e)
            )
            raise VerificationError(
                f"Failed to verify attribute '{attribute}' in {selector}"
            ) from e
