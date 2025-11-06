# QA Automation MCP Server

## Overview

This MCP server exposes our intelligent browser automation Agent as MCP tools, allowing any MCP client (Claude Desktop, Cursor, VS Code with MCP, etc.) to use our QA automation capabilities.

## Architecture

```
┌─────────────────┐
│  MCP Client     │  (Claude Desktop, Cursor, etc.)
│  (Any LLM)      │
└────────┬────────┘
         │ MCP Protocol
         ├─────────────────────────────────┐
         │                                 │
┌────────▼────────┐              ┌────────▼────────┐
│  qa_execute_test│              │ qa_search_product│
└────────┬────────┘              └────────┬────────┘
         │                                │
         └────────────┬───────────────────┘
                      │
            ┌─────────▼──────────┐
            │  Browser Agent     │
            │  (browser-use)     │
            └─────────┬──────────┘
                      │
            ┌─────────▼──────────┐
            │   Chrome Browser   │
            │   (Playwright)     │
            └────────────────────┘
```

## Available Tools

### 1. `qa_execute_test`

Execute any QA test using natural language.

**Input:**
```json
{
  "task": "Navigate to https://example.com and search for laptop",
  "save_screenshot": true
}
```

**Example:**
```
Execute a test: Go to the homepage, search for 'shoes',
click the first result, and verify the product page loaded
```

### 2. `qa_navigate_and_screenshot`

Navigate to a URL and take a screenshot.

**Input:**
```json
{
  "url": "https://example.com"
}
```

**Example:**
```
Navigate to https://thehoffbrand.com and take a screenshot
```

### 3. `qa_search_product`

Search for a product on an e-commerce site.

**Input:**
```json
{
  "site_url": "https://example.com",
  "search_term": "laptop"
}
```

**Example:**
```
Search for 'hat' on https://thehoffbrand.com
```

### 4. `qa_verify_element`

Verify that an element or condition exists on a page.

**Input:**
```json
{
  "url": "https://example.com/cart",
  "expectation": "the shopping cart has items"
}
```

**Example:**
```
Verify that the cart at https://example.com/cart has items
```

## Usage

### Option 1: With Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "qa-automation": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.mcp_server.qa_mcp_server"],
      "env": {
        "PYTHONPATH": "/path/to/ai-lab-night-browser-automation"
      }
    }
  }
}
```

Then in Claude Desktop:
```
Can you use the QA automation tools to test the homepage of thehoffbrand.com?
```

### Option 2: With mcp-use Client

```python
from mcp_use import MCPClient, MCPAgent
from langchain_openai import ChatOpenAI

# Connect to the QA automation server
client = MCPClient.from_config_file("mcp_server_config.json")
llm = ChatOpenAI(model="gpt-4o")
agent = MCPAgent(llm=llm, client=client)

# Use the agent
result = await agent.run(
    "Test the search functionality on thehoffbrand.com"
)
```

### Option 3: Direct Tool Calls

```python
from mcp_use import MCPClient

client = MCPClient.from_config_file("mcp_server_config.json")
session = client.get_session("qa-automation")

# Call a specific tool
result = await session.call_tool(
    name="qa_execute_test",
    arguments={
        "task": "Go to homepage and search for laptop",
        "save_screenshot": True
    }
)
print(result.content[0].text)
```

## Running the Server

### Standalone Mode

```bash
# Run the MCP server directly
uv run python -m src.mcp_server.qa_mcp_server
```

The server will communicate via stdio (standard input/output) using the MCP protocol.

### With Example Client

```bash
# Run the example client that connects to the server
uv run python examples/mcp_client_example.py
```

## Configuration

### Environment Variables

Create a `.env` file with required API keys:

```bash
# Required for the Agent LLM
BROWSER_USE_API_KEY=bu_your_key_here
# OR
ANTHROPIC_API_KEY=sk-ant-your_key_here
# OR
OPENAI_API_KEY=sk-your_key_here

# Optional: Browser settings
HEADLESS_MODE=false
SCREENSHOTS_DIR=./screenshots
```

### Server Configuration

The server uses the same configuration as the standalone Agent:
- Screenshot directory: `./screenshots` (configurable via `SCREENSHOTS_DIR`)
- Headless mode: Based on `HEADLESS_MODE` environment variable
- Browser timeout: Configured via `BROWSER_TIMEOUT`

## Features

### Intelligent Element Finding

The Agent automatically finds elements without needing CSS selectors:
```
Search for 'laptop' → Agent finds search box automatically
Click on first product → Agent identifies the first product visually
```

### Adaptive to DOM Changes

The Agent adapts to page structure changes, making tests more resilient.

### Screenshot Documentation

All tasks automatically save screenshots to the configured directory:
```
screenshots/agent_navigate_to_homepage_1699123456.png
```

### Natural Language Tasks

Write tests in plain English:
```
"Go to the homepage, add a product to cart, proceed to checkout,
and verify the checkout page loaded correctly"
```

## Integration Examples

### With Claude Desktop

```
You: Can you test the shopping cart on thehoffbrand.com?

Claude: I'll use the QA automation tools to test the shopping cart.
[Claude calls qa_execute_test with appropriate task]
```

### With Cursor/VS Code

Install an MCP client extension and configure the server. Then use natural language in your IDE:
```
// Test the login flow on this website
```

### With Custom Client

```python
import asyncio
from mcp_use import MCPClient

async def run_qa_tests():
    client = MCPClient.from_config_file("mcp_server_config.json")
    session = client.get_session("qa-automation")

    # Run multiple tests
    tests = [
        "Navigate to homepage and verify logo",
        "Test search functionality",
        "Add product to cart and verify"
    ]

    for test in tests:
        result = await session.call_tool(
            name="qa_execute_test",
            arguments={"task": test}
        )
        print(f"Test: {test}")
        print(f"Result: {result.content[0].text}\n")

asyncio.run(run_qa_tests())
```

## Troubleshooting

### Server Not Starting

1. Check that all dependencies are installed:
   ```bash
   uv pip install -e .
   ```

2. Verify Python path in configuration:
   ```json
   {
     "env": {
       "PYTHONPATH": "/full/path/to/project"
     }
   }
   ```

### Agent Not Finding Elements

The Agent uses AI to find elements. If it's struggling:
- Make the task description more specific
- Break complex tasks into smaller steps
- Ensure the website is accessible and loaded

### Screenshots Not Saving

Check:
1. `SCREENSHOTS_DIR` is writable
2. `save_screenshot` parameter is set to `true`
3. Task includes "Take a screenshot" in the description

## Comparison with Direct Agent Usage

| Aspect | MCP Server | Direct Agent |
|--------|-----------|--------------|
| **Access** | Any MCP client | Python code only |
| **Flexibility** | Can use from Claude, Cursor, etc. | Single application |
| **Protocol** | Standard MCP | Custom API |
| **Integration** | Easy (add to config) | Manual integration |
| **Use Case** | Multi-client, team use | Single application |

## Advanced Usage

### Custom Tools

Extend the server with custom tools by modifying `qa_mcp_server.py`:

```python
Tool(
    name="qa_custom_test",
    description="Your custom test description",
    inputSchema={
        # Your schema
    }
)
```

### Error Handling

The server catches exceptions and returns them as MCP error responses:
```python
try:
    result = await session.call_tool(...)
except Exception as e:
    print(f"Tool failed: {e}")
```

### Monitoring

Enable debug logging:
```bash
export MCP_LOG_LEVEL=DEBUG
uv run python -m src.mcp_server.qa_mcp_server
```

## Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [mcp-use Documentation](https://github.com/mcp-use/mcp-use)
- [browser-use Documentation](https://docs.browser-use.com/)
- [Agent Guide](AGENT_GUIDE.md) - How the Agent works internally

---

**Team:** Levante Team
**Last Updated:** 2025-11-06
