# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **AI Lab Night experimental repository** for exploring AI-driven browser automation. Teams document their experiments with different browser automation libraries and tackle specific technological challenges related to web automation.

## Repository Structure

- **README.md**: Central documentation listing browser automation libraries, technical challenges, and suggested test websites
- **TEAM-EXPERIMENT.md**: Team-specific documentation for the current experiment (Levante Team)
- **docs/**: Excluded from git (per .gitignore)

## Current Experiment: Levante Team

**Objective**: Automated QA testing of a Shopify store using natural language processing (NLP) and Model Context Protocol (MCP)

**Tech Stack**:
- [mcp-use](https://github.com/mcp-use/mcp-use) - Python library for MCP integration
- [browser-use](https://github.com/browser-use/browser-use) - AI-oriented browser automation library
- Python

## Browser Automation Libraries

The project explores three main libraries for comparison:

1. **browser-use**: LLM-optimized automation with cloud support, session management, and agent control
2. **notte**: Lower-level programmable browser control with fine-grained DOM manipulation
3. **TheAgenticBrowser**: Newer agentic automation for LLM-driven multi-step reasoning

## Working with Experiments

When creating or modifying experiments:

1. **Branch Structure**: Each team should work on their own branch (e.g., `team-levante`)
2. **Documentation**: Update TEAM-EXPERIMENT.md with:
   - Team name and participants
   - Chosen challenge(s) from the 7 categories
   - Tech stack and libraries used
   - Results and conclusions after experimentation

3. **Challenge Selection**: Choose at least one technological challenge:
   - Page Variability & DOM Complexity
   - CAPTCHAs & Bot Detection
   - Authentication & Session Management
   - Performance & Scalability
   - Error Handling & Recovery
   - Long-Horizon Task Planning
   - UI Diversity & Accessibility

## Development Notes

- This is an **exploratory/experimental project** - code will be developed iteratively
- Focus on documenting findings and challenges encountered
- Use test websites from README.md or propose alternatives with justification
- Python is the primary language for automation scripts
- No build/test commands exist yet - they will be added as experiments progress

## Key Resources

Test websites for automation challenges are listed in README.md under "Challenges & Suggested Web Sites".
