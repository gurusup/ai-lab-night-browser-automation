from browser_use import Agent, Browser, ChatBrowserUse
from dotenv import load_dotenv
import os
import asyncio

load_dotenv();

EXPAND_TESTING_FILE = os.getenv("EXPAND_TESTING_FILE")
HUMAN_DETECTION_FILE = os.getenv("HUMAN_DETECTION_FILE")
RESOLVE_CAPTCHA_FILE = os.getenv("RESOLVE_CAPTCHA_FILE")
AUTH_AND_SESSION_MANAGER_FILE = os.getenv("AUTH_AND_SESSION_MANAGER_FILE")
PERFORMANCE_AND_SCALABILITY_FILE = os.getenv("PERFORMANCE_AND_SCALABILITY_FILE")
ERROR_HANDLING_AND_RECOVERY_FILE = os.getenv("ERROR_HANDLING_AND_RECOVERY_FILE")
LONG_HORIZON_TASK_PLANNING_FILE = os.getenv("LONG_HORIZON_TASK_PLANNING_FILE")
UI_DIVERSITY_AND_ACCESSIBILITY_FILE = os.getenv("UI_DIVERSITY_AND_ACCESSIBILITY_FILE")

async def run_test_case(filename):
    browser = Browser(
        # use_cloud=True,  # Uncomment to use a stealth browser on Browser Use Cloud
    )

    llm = ChatBrowserUse()

    with open(filename, "r") as f:
        task_file = f.read()

    agent = Agent(
        task=task_file,
        llm=llm,
        browser=browser,
    )

    history = await agent.run()
    return history

if __name__ == "__main__":
    history = asyncio.run(run_test_case(RESOLVE_CAPTCHA_FILE))