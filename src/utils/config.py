"""Configuration management for the QA automation system."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Load environment variables
load_dotenv()

# Get project root directory (two levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()


class Config(BaseModel):
    """Application configuration."""

    # LLM Configuration
    openai_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    anthropic_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    browser_use_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("BROWSER_USE_API_KEY")
    )

    # Shopify Store Configuration
    shopify_store_url: str = Field(
        default_factory=lambda: os.getenv(
            "SHOPIFY_STORE_URL", "https://your-store.myshopify.com"
        )
    )
    shopify_test_user_email: Optional[str] = Field(
        default_factory=lambda: os.getenv("SHOPIFY_TEST_USER_EMAIL")
    )
    shopify_test_user_password: Optional[str] = Field(
        default_factory=lambda: os.getenv("SHOPIFY_TEST_USER_PASSWORD")
    )

    # Browser Configuration
    headless_mode: bool = Field(
        default_factory=lambda: os.getenv("HEADLESS_MODE", "false").lower() == "true"
    )
    browser_timeout: int = Field(
        default_factory=lambda: int(os.getenv("BROWSER_TIMEOUT", "30000"))
    )
    screenshots_dir: Path = Field(
        default_factory=lambda: (
            Path(os.getenv("SCREENSHOTS_DIR"))
            if os.getenv("SCREENSHOTS_DIR")
            else PROJECT_ROOT / "screenshots"
        )
    )

    # MCP Server Configuration
    mcp_server_port: int = Field(
        default_factory=lambda: int(os.getenv("MCP_SERVER_PORT", "8080"))
    )
    mcp_log_level: str = Field(
        default_factory=lambda: os.getenv("MCP_LOG_LEVEL", "INFO")
    )

    def __init__(self, **data):
        """Initialize configuration and create necessary directories."""
        super().__init__(**data)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
