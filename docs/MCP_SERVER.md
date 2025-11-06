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
         │ (stdio)
         │
┌────────▼────────┐
│  qa_automation  │  Single Tool
│                 │  Accepts natural language
└────────┬────────┘
         │
         │
┌────────▼────────┐
│  Browser Agent  │  Intelligent automation
│  (browser-use)  │  Finds elements automatically
└────────┬────────┘
         │
┌────────▼────────┐
│ Chrome Browser  │  Actual browser interaction
│  (Playwright)   │
└─────────────────┘
```

## Available Tool

### `qa_automation`

Execute any browser automation task using natural language instructions. This single, powerful tool handles all web automation scenarios through the intelligent Agent.

**Input:**
```json
{
  "instruction": "Search for SEVEN RUNNER METALLIC COPPER on https://thehoffbrand.com/, add it to cart and generate screenshot"
}
```

**What it can do:**
- Navigate to any URL
- Search for products
- Click elements, fill forms
- Add items to cart
- Verify elements exist
- Take screenshots
- Execute multi-step workflows
- Handle dynamic content

**Examples:**

**Simple Navigation:**
```json
{
  "instruction": "Navigate to https://thehoffbrand.com and take a screenshot"
}
```

**Product Search:**
```json
{
  "instruction": "Go to https://example.com, search for 'laptop', and capture the results"
}
```

**Complex Workflow:**
```json
{
  "instruction": "Search for SEVEN RUNNER METALLIC COPPER on https://thehoffbrand.com/, add it to cart and generate screenshot"
}
```

**Element Verification:**
```json
{
  "instruction": "Go to https://example.com/cart and verify that the shopping cart has items"
}
```

**Multi-step Test:**
```json
{
  "instruction": "Navigate to the homepage, search for 'shoes', click the first result, verify the product page loaded, and take a screenshot"
}
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
Search for SEVEN RUNNER METALLIC COPPER on https://thehoffbrand.com/,
add it to cart and generate screenshot
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

# Call the automation tool
result = await session.call_tool(
    name="qa_automation",
    arguments={
        "instruction": "Search for SEVEN RUNNER METALLIC COPPER on https://thehoffbrand.com/, add it to cart and generate screenshot"
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
You: Search for SEVEN RUNNER METALLIC COPPER on https://thehoffbrand.com/,
     add it to cart and generate screenshot

Claude: I'll use the QA automation tool to search for that product and add it to cart.
[Claude calls qa_automation with your instruction]
```

### With Cursor/VS Code

Install an MCP client extension and configure the server. Then use natural language in your IDE:
```
Search for 'laptop' on https://example.com and add the first one to cart
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
        "Navigate to https://thehoffbrand.com and verify the logo is visible",
        "Search for 'hat' and verify results appear",
        "Go to https://thehoffbrand.com, search for 'shirt', add first product to cart"
    ]

    for test in tests:
        result = await session.call_tool(
            name="qa_automation",
            arguments={"instruction": test}
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
2. The Agent automatically takes screenshots at key moments
3. Mention "screenshot" in your instruction if you want explicit captures

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
