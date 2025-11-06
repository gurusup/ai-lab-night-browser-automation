# Agent vs. Traditional Automation Guide

This project now supports **TWO approaches** to browser automation:

## 🤖 Approach 1: Intelligent Agent (Recommended)

**File:** `AgentMCPServer` ([agent_server.py](src/mcp_server/agent_server.py))

### How It Works
Uses browser-use's **Agent** with AI to:
- ✅ **Automatically find elements** (no selectors needed!)
- ✅ **Adapt to DOM changes** (works even if page updates)
- ✅ **Visual analysis** (understands page layout)
- ✅ **Intelligent decisions** (figures out what to click)
- ✅ **Self-healing** (recovers from errors)

### When to Use
- Testing **dynamic websites** with changing layouts
- **Exploratory testing** where you don't know selectors
- **Cross-site testing** with different structures
- When you want **maximum adaptability**
- **Proof of concepts** and demos

### Trade-offs
- ⚡ **Slower** (uses AI for each action)
- 💰 **More expensive** (more API calls)
- 🎯 **Less predictable** (AI makes decisions)

### Example

```python
from src.mcp_server import AgentMCPServer

async with AgentMCPServer(headless=False) as server:
    result = await server.execute_test("""
        Go to the homepage
        Find the search box and search for 'laptop'
        Click on the first product
        Add it to the cart
    """)
```

**The Agent figures out everything!** No selectors, no DOM knowledge needed.

---

## ⚡ Approach 2: Traditional Automation (Faster)

**File:** `MCPServer` ([server.py](src/mcp_server/server.py))

### How It Works
Uses **Playwright** directly with:
- 🎯 **Fixed CSS selectors** (you specify exactly what to click)
- ⚡ **Direct DOM manipulation** (no AI, just code)
- 📋 **Predefined actions** (search, click, fill, etc.)
- 🔄 **Fallback selectors** (tries multiple options)

### When to Use
- Testing **stable pages** with consistent selectors
- **Performance-critical** scenarios
- **Budget-conscious** projects
- **Regression testing** with known flows
- When you need **speed and reliability**

### Trade-offs
- 🔧 **Requires selector knowledge** (need to know HTML structure)
- 🚫 **Breaks on DOM changes** (if selectors change, tests fail)
- 📝 **More code** (need to handle each scenario)

### Example

```python
from src.mcp_server import MCPServer

async with MCPServer(use_browser_use=True, headless=False) as server:
    result = await server.execute_test("""
        Go to homepage
        Search for 'laptop'
        Click first product
        Add to cart
    """)
```

Uses predefined Shopify selectors in [shopify.py](src/automation/shopify.py).

---

## 📸 Screenshot Handling

### How Screenshots Work with Agent

The browser-use Agent **automatically takes screenshots** during execution and stores them in the history object. Our implementation automatically saves these screenshots to disk.

#### Screenshot Workflow

1. **Agent captures screenshots** during task execution (when requested or at decision points)
2. **Screenshots are stored** in the Agent's history as base64 or file paths
3. **Our code automatically saves** them to `./screenshots/` with descriptive names
4. **Results include paths** to all saved screenshots

#### Example Usage

```python
from src.mcp_server.agent_server import AgentMCPServer

async with AgentMCPServer(headless=False) as server:
    result = await server.execute_test("""
        Navigate to https://example.com
        Take a screenshot of the homepage
        Search for 'product'
        Take another screenshot of the results
    """)

    # Screenshots are automatically saved
    print(f"Saved {len(result.screenshots)} screenshots:")
    for screenshot_path in result.screenshots:
        print(f"  📸 {screenshot_path}")

    # Example output:
    # 📸 screenshots/agent_navigate_to_https_example_com_1699123456.png
    # 📸 screenshots/agent_search_for_product_1699123467.png
```

#### Screenshot Methods

The implementation tries three methods in order:

```python
# Method 1: Use screenshot paths if Agent already saved them
paths = history.screenshot_paths()  # Returns file paths

# Method 2: Get base64 screenshots and save them
screenshots = history.screenshots()  # Returns base64 strings
# → We decode and save to disk

# Method 3: Manual fallback screenshot
# → If history has no screenshots, we take one manually
```

#### When Agent Takes Screenshots

The Agent captures screenshots:
- ✅ When **explicitly requested** in task ("Take a screenshot")
- ✅ When **`use_vision=True`** is enabled (for visual analysis)
- ✅ At **key decision points** during execution (optional)

#### Screenshot Filenames

Format: `agent_{task_description}_{timestamp}.png`

Examples:
- `agent_navigate_to_homepage_1699123456.png`
- `agent_search_for_laptop_1699123467.png`
- `agent_click_first_product_1699123478.png`

#### Important Notes

1. **Always include "Take a screenshot"** in your task if you want guaranteed screenshots
2. **All screenshots are collected** in `result.screenshots[]` list
3. **Location**: Configured via `SCREENSHOTS_DIR` env var (default: `./screenshots`)
4. **Format**: PNG with descriptive names and timestamps
5. **Automatic cleanup**: Not implemented - manage old screenshots manually

---

## 📊 Comparison

| Feature | Agent (Intelligent) | Traditional (Fast) |
|---------|-------------------|-------------------|
| **Speed** | 🐌 Slower (AI processing) | ⚡ Fast (direct actions) |
| **Cost** | 💰💰 Higher ($0.20-2.00 per 1M tokens) | 💰 Lower (minimal API calls) |
| **Adaptability** | 🌟 Excellent (finds elements automatically) | ⚠️ Limited (needs exact selectors) |
| **Maintenance** | ✅ Low (adapts to changes) | 🔧 High (update selectors) |
| **Reliability** | 🎲 Variable (AI decisions) | ✅ Consistent (deterministic) |
| **Setup** | 🚀 Easy (just describe in NL) | 📝 Complex (write selectors) |
| **Use Case** | Exploratory, dynamic sites | Regression, stable sites |

---

## 🎯 Choosing the Right Approach

### Use **Agent** when:
- ✅ Testing a site you don't know well
- ✅ Site layout changes frequently
- ✅ You want quick proof of concepts
- ✅ Budget allows for AI costs
- ✅ Adaptability > speed

### Use **Traditional** when:
- ✅ You know the site structure
- ✅ Selectors are stable
- ✅ Speed is critical
- ✅ Budget is limited
- ✅ Need deterministic behavior

---

## 🔄 Hybrid Approach (Best of Both)

You can **mix both**:

```python
# Use Agent for exploration
from src.mcp_server import AgentMCPServer

async with AgentMCPServer() as agent_server:
    # Agent figures out the site
    await agent_server.execute_test("Explore the homepage and find all products")

# Then use Traditional for regression tests
from src.mcp_server import MCPServer

async with MCPServer() as fast_server:
    # Fast, deterministic tests with known selectors
    await fast_server.execute_test("Navigate to homepage and verify logo")
```

---

## 📁 File Structure

```
src/
├── automation/
│   ├── browser.py           # Traditional: Playwright automation
│   ├── browser_agent.py     # Intelligent: Agent automation  ⭐ NEW
│   ├── shopify.py           # Traditional: Shopify-specific actions
│   └── verifications.py     # Traditional: Test assertions
├── mcp_server/
│   ├── server.py            # Traditional MCP Server
│   ├── agent_server.py      # Agent MCP Server  ⭐ NEW
│   ├── parser.py            # NL parser (for traditional)
│   └── actions.py           # Action definitions (for traditional)
```

---

## 🚀 Getting Started

### Option 1: Intelligent Agent

```bash
python examples/agent_basic_test.py
```

### Option 2: Traditional Automation

```bash
python examples/basic_test.py
```

---

## 💡 Examples

### Agent Example (Intelligent)

```python
# Agent automatically finds and uses search box
result = await agent_server.execute_test("""
    Find the search functionality on the page
    Search for 'laptop'
    Click on the highest rated product
    Verify price is reasonable
""")
```

### Traditional Example (Fast)

```python
# Uses predefined selectors
result = await server.execute_test("""
    Navigate to homepage
    Search for 'laptop'
    Click first product
    Verify product page loaded
""")
```

---

## 🎓 Learning More

- **Agent Documentation**: [Browser-use Docs](https://docs.browser-use.com/)
- **Traditional (Playwright)**: [Playwright Docs](https://playwright.dev/)
- **Project PRD**: [exclude/PRD.md](exclude/PRD.md)

---

## 🤝 Contributing

When adding new features, consider:

1. **Agent**: Add natural language task descriptions
2. **Traditional**: Add specific actions and selectors

Both approaches are valuable for different scenarios!

---

**Team:** Levante Team
**Last Updated:** 2025-11-06
**Status:** Experimental - Both approaches available
