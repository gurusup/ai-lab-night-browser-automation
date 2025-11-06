# AI Lab Night: AI Browser Automation

## Overview

This project explores browser automation using leading AI-oriented libraries that enable programmatic website interaction, data gathering, and multi-step automation through LLM agents and scripts.

### Leading Libraries

#### 1. [Browser Use (browser-use)](https://github.com/browser-use/browser-use)
- Python package for making websites accessible for AI agents and automating online tasks.
- Optimized for LLMs (OpenAI, Claude, local, etc.), with built-in agent control, cloud/infrastructure scaling features, and demo-rich templates.
- Strengths: Fast setup, session/auth management, cloud + local support, extensible via agent tools, robust docs & community.
- Challenges: Resource scaling locally, API key required for full feature set, countering CAPTCHAs/anti-bot measures, adapting to web updates.

#### 2. [Notte (nottelabs/notte)](https://github.com/nottelabs/notte)
- Python automation library for robust, programmable, and headless browser control (page/DOM/element level).
- Suited to researchers and advanced scripting, as well as agent-based abstraction, though less LLM-ready out of the box.
- Strengths: Fine-grained control, stable Python APIs.
- Challenges: Smaller ecosystem, less-focused on agentic templates/workflows.

#### 3. [TheAgenticBrowser](https://github.com/TheAgenticAI/TheAgenticBrowser)
- Newer agentic browser automation targeting LLM-driven, multi-step reasoning and modern web app interaction.
- Optimized for explorative/complex web tasks.
- Strengths: Design for AI agents, advanced selectors, unstructured task workflow.
- Challenges: Early stage, fewer integrations/examples, APIs may change quickly.

---

## Key Technical Challenges for Good-Quality Implementations

1. **Page Variability & DOM Complexity**  
   - Dynamic content, changing selectors, and complex page structures require robust, adaptive element selection (semantic or ML-based).
2. **CAPTCHAs & Bot Detection**  
   - Sites block bots aggressively; good frameworks use stealth techniques or rotate cloud browsers/fingerprints.
3. **Authentication & Session Management**  
   - Handling logins, MFA, session syncing, and browser profile use gracefully and securely.
4. **Performance & Scalability**  
   - Managing resource-heavy browsers for parallel jobs; cloud infrastructure for scale.
5. **Error Handling & Recovery**  
   - Navigating unexpected modals/pop-ups, retry logic, self-healing scripts with LLM assistance.
6. **Long-Horizon Task Planning**  
   - Agentic automation often requires multi-step memory, branching, and cross-site workflows.
7. **UI Diversity & Accessibility**  
   - Support for accessible components, multiple devices/locales, and differing layouts.
8. **Developer Experience**  
   - Rapid onboarding, clear APIs, extendibility, real code samples, and active community support.

---

## Comparison Table

| Library                    | Agentic APIs | Cloud Support | CAPTCHA Handling | Local Models | Custom Tools | Docs/Community |
|----------------------------|--------------|---------------|------------------|--------------|--------------|----------------|
| browser-use                | Yes          | Yes           | Yes (stealth)    | Yes          | Yes          | Strong         |
| nottelabs/notte            | Partial      | No            | No               | Yes          | Yes          | Growing        |
| TheAgenticBrowser          | Yes          | WIP           | WIP              | No      | Planned      | Early Stage    |

---

## Resources

### Libraries
- [Browser Use Github](https://github.com/browser-use/browser-use)
- [Notte Github](https://github.com/nottelabs/notte)
- [TheAgenticBrowser Github](https://github.com/TheAgenticAI/TheAgenticBrowser)

### Web Resources
- [Testing Scenarios](https://practice.expandtesting.com/)
- [Bot detection](https://pixelscan.net/bot-check)
- [QA Automation Platform](https://www.learnaqa.info)
- [Captchas](https://es.sporcle.com/games/WillieG/crazy-captchas)
- [Test Scenarios](https://automationexercise.com/)

---

## Challenges & Suggested Web Sites

Below are the technological challenge categories along with suggested websites for automation. Participants should select **at least one** of these challenge types (or more for a strong submission), document their choice, strategy, and outcomes.

| #  | Technological Challenge                         | Suggested Web Site & URL                                                                 | Description                                                                                               | Estimated Difficulty | Bonus                             |
|----|------------------------------------------------|-------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|----------------------|------------------------------------------------|
| 1  | **Page Variability & DOM Complexity**           | [Expand Testing](https://practice.expandtesting.com) | Automate a site with dynamic content, non-static selectors, or lazy-loaded lists. Tag: *robustness to selector changes, dynamic lists, lazy-loading*. | Medium              | Agent adapts to DOM changes automatically     |
| 2  | **CAPTCHAs & Bot Detection**                    | [Don't be detected](https://pixelscan.net/bot-check) <br>[Resolve the captcha](https://es.sporcle.com/games/WillieG/crazy-captchas)  | Automate a flow that triggers anti-bot detection or CAPTCHA. Tag: *How does the library handle or avoid detection?* | Hard                | Agent detects or reports CAPTCHA and handles it gracefully |
| 3  | **Authentication & Session Management**         | [Automation Exercise](https://automationexercise.com/)| Automate a login flow (username, password, possible MFA) + session persistence. Tag: *session management, profile reuse, cookie reuse*. | Medium              | 2 hours        | Session reused across runs / cookies persisted |
| 4  | **Performance & Scalability**                   | (Use any suitable site to run multiple agent instances in parallel)                        | Execute multiple parallel automation agents/tabs and evaluate resource limits. Tag: *scalability, concurrency, resource consumption*. | Hard                | 10+ parallel agents run with stability         |
| 5  | **Error Handling & Recovery**                   | (Pick a site with pop-ups, modals, unexpected navigation)                                 | Script a flow including unexpected elements (modals/pop-ups). Tag: *agent’s resilience, retry logic, logging*.        | Medium–Hard         | Agent recovers from 2+ unexpected errors      |
| 6  | **Long-Horizon Task Planning**                  | [Automation Exercise](https://automationexercise.com/)| Build a multi-step, multi-page workflow (e.g., signup → login → shop → checkout) and track state. Tag: *multi-step planning, agent memory, state management*. | Hard                | Flow spans 4+ pages with state tracked        |
| 7  | **UI Diversity & Accessibility**                | (Select a site with responsive/mobile layouts, localization, accessibility features)       | Automate across diverse UI layouts (mobile vs desktop) or localization/accessibility. Tag: *layout adaptation, mobile support, ARIA elements*. | Medium              | Agent handles mobile viewport and localized UI |

> 🔍 _Note:_ The suggested web sites are a starting point; participants may propose **other** web sites and challenges provided they clearly explain why the selected site meets the technological challenge. Participants must cite the URL, justify the match to the challenge, and document any limitations or risks found.

---

## Levante Team Experiment

This repository includes a complete implementation by Levante Team:

- **[Team Experiment](TEAM-EXPERIMENT.md)** - Team info and challenge selection
- **[Project Documentation](docs/PROJECT_README.md)** - Complete project details
- **[Agent Guide](docs/AGENT_GUIDE.md)** - Agent vs Traditional automation comparison
- **[Usage Guide](docs/USAGE.md)** - How to use the QA automation system
- **[PRD](docs/exclude/PRD.md)** - Product requirements document

### Quick Start

```bash
# Install dependencies
uv pip install -e .

# Configure environment
cp .env.example .env
# Add your API keys to .env

# Run the Agent-based automation
uv run python examples/agent_basic_test.py

# Run traditional automation
uv run python examples/basic_test.py
```

