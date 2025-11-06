# Shopify QA Automation with MCP and NLP

Automated Quality Assurance testing system for Shopify stores using natural language processing and the Model Context Protocol (MCP).

## Overview

This project enables QA testers to write and execute automated tests using natural language commands. The system uses:

- **mcp-use**: Python library for MCP integration
- **browser-use**: AI-driven browser automation
- **LangChain**: Natural language parsing with Claude or GPT-4
- **Playwright**: Underlying browser control

## Quick Start

### 1. Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .

# Install Playwright browsers
playwright install
```

### 2. Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`: For natural language parsing
- `BROWSER_USE_API_KEY`: For browser-use features
- `SHOPIFY_STORE_URL`: Your test Shopify store URL

### 3. Run Example Tests

```bash
# Basic examples
python examples/basic_test.py

# Shopify-specific scenarios
python examples/shopify_scenarios.py
```

## Project Structure

```
src/
├── mcp_server/          # MCP server implementation
│   ├── server.py        # Main MCP server
│   ├── parser.py        # Natural language parser
│   └── actions.py       # Action definitions and executor
├── automation/          # Browser automation
│   ├── browser.py       # Core browser automation
│   ├── shopify.py       # Shopify-specific actions
│   └── verifications.py # Test assertions
└── utils/              # Utilities
    ├── logger.py        # Logging configuration
    └── config.py        # Configuration management

examples/               # Example test scripts
tests/                 # Unit tests (TBD)
docs/exclude/          # Project documentation (PRD, etc.)
```

## Usage

### Basic Usage

```python
import asyncio
from src.mcp_server import MCPServer

async def main():
    # Create and start server
    async with MCPServer(use_anthropic=True, headless=False) as server:
        # Execute a test in natural language
        result = await server.execute_test("""
            Test the product search:
            1. Go to the homepage
            2. Search for 'laptop'
            3. Verify results are shown
            4. Take a screenshot
        """)

        print(f"Test Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Screenshots: {result.screenshots}")

asyncio.run(main())
```

### Using Direct Actions

```python
from src.mcp_server import MCPServer
from src.mcp_server.actions import Action, ActionType

async def main():
    async with MCPServer() as server:
        actions = [
            Action(ActionType.NAVIGATE, {"url": "homepage"}, "Go home"),
            Action(ActionType.SEARCH, {"term": "laptop"}, "Search"),
            Action(ActionType.SCREENSHOT, {}, "Capture"),
        ]

        result = await server.execute_actions(actions)
        print(f"Result: {result.status}")

asyncio.run(main())
```

## Natural Language Examples

The system understands various natural language commands:

### Navigation
- "Go to the homepage"
- "Navigate to homepage"
- "Visit the store"

### Search
- "Search for 'laptop'"
- "Search for blue t-shirt"

### Cart Operations
- "Add to cart"
- "Add product to cart"
- "Go to cart"
- "Proceed to checkout"

### Product Variants
- "Select size Medium"
- "Choose color Blue"

### Verifications
- "Verify the page contains 'laptop'"
- "Check that the URL contains 'cart'"
- "Verify element with selector '.product-title' is present"

### Screenshots
- "Take a screenshot"
- "Capture the page"

## Available Actions

### Core Actions
- `navigate`: Navigate to URL or homepage
- `search`: Search for products
- `click`: Click elements
- `fill`: Fill input fields
- `screenshot`: Take screenshots

### Shopify-Specific Actions
- `add_to_cart`: Add product to cart
- `go_to_cart`: Navigate to cart
- `checkout`: Proceed to checkout
- `select_variant`: Select product variant (size, color)

### Verification Actions
- `verify_text`: Verify text content
- `verify_element`: Verify element presence
- `verify_url`: Verify URL contains text

## Test Results

Test results include:
- **Status**: `passed`, `failed`, or `error`
- **Duration**: Execution time in milliseconds
- **Actions Executed**: Detailed log of each action
- **Screenshots**: Paths to captured screenshots
- **Errors**: List of any errors encountered

Example result:
```python
{
    "status": "passed",
    "passed": True,
    "duration_ms": 5432,
    "actions_executed": [
        {"action": "navigate", "status": "success"},
        {"action": "search", "status": "success"},
    ],
    "screenshots": ["./screenshots/step_1.png"],
    "errors": []
}
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:
- `HEADLESS_MODE`: Run browser in headless mode (true/false)
- `BROWSER_TIMEOUT`: Timeout for browser operations (ms)
- `SCREENSHOTS_DIR`: Directory for screenshots
- `MCP_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Browser Configuration

The browser automation supports:
- Headless/headed modes
- Custom timeouts
- Screenshot capture
- Session management
- Cookie persistence

## Logging

The system uses `structlog` for structured logging:

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Test started", test_name="product_search")
```

Logs include:
- Timestamps
- Log levels
- File/function names
- Structured context data

## Development

### Adding New Actions

1. Add action type to `ActionType` enum in `actions.py`
2. Create handler method in `ActionExecutor`
3. Update parser to recognize the action (optional)

Example:
```python
# In actions.py
class ActionType(Enum):
    MY_ACTION = "my_action"

# In ActionExecutor
async def _handle_my_action(self, action: Action) -> Dict[str, Any]:
    # Implementation
    return {"result": "success"}
```

### Running Tests

```bash
# Run all examples
python examples/basic_test.py
python examples/shopify_scenarios.py

# Run with different configurations
HEADLESS_MODE=true python examples/basic_test.py
MCP_LOG_LEVEL=DEBUG python examples/shopify_scenarios.py
```

## Troubleshooting

### Browser fails to start
- Ensure Playwright browsers are installed: `playwright install`
- Check if ports are available
- Try running in headed mode: `HEADLESS_MODE=false`

### Natural language parsing errors
- Verify API keys are set in `.env`
- Check internet connectivity
- Try rule-based parsing (set both API keys to empty)

### Selector not found errors
- Take screenshots to debug: Add "Take a screenshot" step
- Check selector in browser DevTools
- Use more specific or alternative selectors
- Wait for dynamic content to load

### Rate limiting
- Add delays between actions
- Use local LLM models for parsing (if available)
- Cache parsed actions

## Performance Tips

1. **Use headless mode** for faster execution
2. **Batch tests** to reuse browser sessions
3. **Cache parsed actions** for repeated tests
4. **Optimize selectors** for faster element location
5. **Use rule-based parsing** when possible (faster than LLM)

## Contributing

This is an experimental project for AI Lab Night. To contribute:

1. Create a feature branch
2. Document your changes
3. Add examples for new features
4. Update tests
5. Submit for review

## Resources

- [mcp-use Documentation](https://github.com/mcp-use/mcp-use)
- [browser-use Documentation](https://github.com/browser-use/browser-use)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Project PRD](docs/exclude/PRD.md)

## License

This project is for educational and experimental purposes as part of AI Lab Night.

---

**Team**: Levante Team
**Participant**: Oliver Montes
**Last Updated**: 2025-11-06
