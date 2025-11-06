# Usage Guide

Quick guide to using the Shopify QA Automation system.

## Quick Start

### 1. Setup

```bash
# Install dependencies
uv pip install -e .

# Install Playwright browsers
playwright install

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### 2. Run Tests

#### Interactive Mode

```bash
python run_test.py
```

Then enter test instructions in natural language:
```
> Enter test instruction: Go to homepage and search for laptop

Executing test...
========================================
Status: passed | Duration: 3421ms
========================================
✓ 1. navigate
✓ 2. search
```

#### Command Line Mode

```bash
python run_test.py "Go to homepage, search for laptop, and take a screenshot"
```

#### Using Example Scripts

```bash
# Basic examples
python examples/basic_test.py

# Shopify scenarios
python examples/shopify_scenarios.py
```

## Natural Language Examples

### Simple Navigation
```
Go to the homepage
```

### Product Search
```
Search for 'laptop'
```

### Complete Flow
```
Test the purchase flow:
1. Go to homepage
2. Search for 'blue t-shirt'
3. Click first product
4. Select size Medium
5. Add to cart
6. Go to cart
7. Take screenshot
```

### With Validation
```
Validate search works:
1. Go to homepage
2. Search for 'laptop'
3. Verify URL contains 'search'
4. Verify page contains 'laptop'
5. Take screenshot
```

## Programmatic Usage

### Basic Test

```python
import asyncio
from src.mcp_server import MCPServer

async def main():
    async with MCPServer() as server:
        result = await server.execute_test("""
            Go to homepage and search for laptop
        """)

        print(f"Status: {result.status}")
        print(f"Duration: {result.duration_ms}ms")

asyncio.run(main())
```

### With Error Handling

```python
async def safe_test():
    try:
        async with MCPServer(use_anthropic=True, headless=False) as server:
            result = await server.execute_test("Your test here")

            if result.passed:
                print("✓ Test passed!")
            else:
                print("✗ Test failed:")
                for error in result.errors:
                    print(f"  - {error}")

            # Access screenshots
            for screenshot in result.screenshots:
                print(f"Screenshot: {screenshot}")

    except Exception as e:
        print(f"Error: {e}")

asyncio.run(safe_test())
```

### Custom Actions

```python
from src.mcp_server import MCPServer
from src.mcp_server.actions import Action, ActionType

async def custom_actions_test():
    async with MCPServer() as server:
        actions = [
            Action(
                ActionType.NAVIGATE,
                {"url": "homepage"},
                "Navigate to homepage"
            ),
            Action(
                ActionType.SEARCH,
                {"term": "laptop"},
                "Search for laptop"
            ),
            Action(
                ActionType.SCREENSHOT,
                {"name": "search_results"},
                "Capture results"
            ),
        ]

        result = await server.execute_actions(actions)
        return result

asyncio.run(custom_actions_test())
```

## Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Required: At least one LLM API key
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Required: Browser-use API key
BROWSER_USE_API_KEY=bu_...

# Required: Shopify store URL
SHOPIFY_STORE_URL=https://your-store.myshopify.com

# Optional: Browser settings
HEADLESS_MODE=false
BROWSER_TIMEOUT=30000
SCREENSHOTS_DIR=./screenshots

# Optional: Server settings
MCP_LOG_LEVEL=INFO
```

### Runtime Configuration

```python
# Use OpenAI instead of Anthropic
server = MCPServer(use_anthropic=False)

# Run in headless mode
server = MCPServer(headless=True)

# Both
server = MCPServer(use_anthropic=False, headless=True)
```

## Available Actions

### Navigation
- `navigate` - Go to URL or homepage
  - `{"url": "homepage"}` or `{"url": "https://..."}`

### Search
- `search` - Search for products
  - `{"term": "laptop"}`

### Interaction
- `click` - Click element
  - `{"selector": ".button-class"}`
- `fill` - Fill input field
  - `{"selector": "#email", "text": "test@example.com"}`

### Cart Operations
- `add_to_cart` - Add product to cart
- `go_to_cart` - Navigate to cart
- `checkout` - Proceed to checkout

### Product Selection
- `select_variant` - Select product variant
  - `{"type": "Size", "value": "Medium"}`

### Verification
- `verify_text` - Verify text present
  - `{"selector": ".title", "text": "expected"}`
- `verify_element` - Verify element exists
  - `{"selector": ".product"}`
- `verify_url` - Verify URL contains
  - `{"url": "cart"}`

### Utilities
- `screenshot` - Take screenshot
  - `{"name": "optional_name"}`

## Tips

### 1. Use Screenshots for Debugging
```python
result = await server.execute_test("""
    Go to homepage
    Take screenshot
    Search for laptop
    Take screenshot
""")

for screenshot in result.screenshots:
    print(f"See: {screenshot}")
```

### 2. Verify Your Actions
```python
await server.execute_test("""
    Add product to cart
    Go to cart
    Verify URL contains 'cart'
    Verify element '.cart-item' is present
""")
```

### 3. Handle Errors Gracefully
```python
result = await server.execute_test("Your test")

if not result.passed:
    # Check what failed
    for action in result.actions_executed:
        if action['status'] == 'error':
            print(f"Failed: {action['action']}")
```

### 4. Use Headless Mode for Speed
```python
# Development: see what's happening
server = MCPServer(headless=False)

# CI/Production: faster execution
server = MCPServer(headless=True)
```

### 5. Batch Tests
```python
async with MCPServer() as server:
    # Reuse same browser session
    result1 = await server.execute_test("Test 1")
    result2 = await server.execute_test("Test 2")
    result3 = await server.execute_test("Test 3")
```

## Troubleshooting

### Issue: Browser won't start
```bash
# Reinstall Playwright browsers
playwright install
```

### Issue: Selector not found
```python
# Add screenshot before failing action
"""
Take screenshot
Click element '.my-selector'
"""
```

### Issue: Slow parsing
```python
# Use rule-based parsing (faster, less accurate)
# Don't set LLM API keys, or:
server = MCPServer(use_anthropic=False)
# with OPENAI_API_KEY unset
```

### Issue: Rate limits
```python
# Add delays
import asyncio

await server.execute_test("Action 1")
await asyncio.sleep(2)  # Wait 2 seconds
await server.execute_test("Action 2")
```

## Examples

### E-commerce Full Flow
```python
result = await server.execute_test("""
    Test complete purchase flow:
    1. Navigate to homepage
    2. Search for 'laptop'
    3. Click first product
    4. Select variant 'Size: Medium'
    5. Add to cart
    6. Go to cart
    7. Verify cart has items
    8. Proceed to checkout
    9. Take screenshot of checkout
""")
```

### Search Validation
```python
result = await server.execute_test("""
    Validate search:
    1. Go to homepage
    2. Search for 'laptop'
    3. Verify URL contains 'search'
    4. Verify page contains 'laptop'
    5. Take screenshot
""")
```

### Multi-Product Cart
```python
result = await server.execute_test("""
    Add multiple products:
    1. Go to homepage
    2. Search for 'laptop'
    3. Add to cart
    4. Go to homepage
    5. Search for 'mouse'
    6. Add to cart
    7. Go to cart
    8. Verify multiple items
""")
```

## More Information

- [Project README](PROJECT_README.md) - Full documentation
- [Agent Guide](AGENT_GUIDE.md) - Agent vs Traditional automation
- [PRD](exclude/PRD.md) - Product requirements
- [Examples](../examples/) - More code examples

---

Need help? Check the logs in console (structured JSON format) or set `MCP_LOG_LEVEL=DEBUG` for detailed output.
