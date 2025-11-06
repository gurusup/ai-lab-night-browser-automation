#!/usr/bin/env python3

import os
import re
import asyncio
from datetime import datetime
import requests

try:
    from dotenv import load_dotenv
    load_dotenv("config.env")
except Exception:
    pass

from browser_use import Agent, Browser, ChatBrowserUse


EXCLUDED_SITES: list[str] = [
    "empresite.eleconomista.es", "infonif.economia3.com", "cincodias.elpais.com", "infojobs.net",
    "expansion.com", "einforma.com", "datoscif.es", "es.linkedin.com", "axesor.es", "iberinform.es",
    "qdq.com", "empresia.es", "infoempresa.com", "goodreads.com", "cleartrip.com", "linkedin.com",
    "facebook.com", "instagram.com",
]


def build_google_search_query(company_name: str) -> str:
    query = f'"{company_name}"'
    for site in EXCLUDED_SITES:
        query += f" -site:{site}"
    return query


def get_public_ip() -> str:
    services = ["https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com", "https://ident.me"]
    for service in services:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                ip = response.text.strip()
                if ip: return ip
        except Exception:
            continue
    return "Unable to determine"


def extract_text_from_history(history: object) -> str:
    try:
        if hasattr(history, "final_result") and history.final_result:
            return str(history.final_result)
        if hasattr(history, "answer") and history.answer:
            return str(history.answer)
        if isinstance(history, list):
            parts: list[str] = []
            for item in history:
                if hasattr(item, "content"):
                    parts.append(str(getattr(item, "content")))
                elif isinstance(item, dict):
                    for key in ("content", "text", "summary", "answer"):
                        if key in item and item[key]:
                            parts.append(str(item[key]))
                            break
                else:
                    parts.append(str(item))
            return "\n".join(parts)
    except Exception:
        pass
    return str(history)


def is_excluded(url: str) -> bool:
    hostname = url.lower()
    return any(excluded in hostname for excluded in EXCLUDED_SITES)


async def search_company_website(company_name: str = "YES IBERIA SL") -> str:
    search_query = build_google_search_query(company_name)
    google_search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

    print(f"Searching for: {company_name}")
    print(f"Query: {search_query}")
    print(f"Google URL: {google_search_url}")
    print("-" * 80)

    browser = Browser(use_cloud=True)
    llm = ChatBrowserUse()
    task = (
        f"Start at: {google_search_url}\n"
        f"Ignore and do not select any result from these domains: {', '.join(EXCLUDED_SITES)}.\n"
        f"Find the official website of '{company_name}' from the search results.\n"
        f"Return ONLY the official company website URL as the final answer."
    )
    agent = Agent(task=task, llm=llm, browser=browser)

    print("Agent is processing the search...")
    history = await agent.run()

    print("\n" + "=" * 80)
    print("AGENT HISTORY / OUTPUT:")
    print("=" * 80)
    history_text = extract_text_from_history(history)
    
    timestamp = datetime.now().strftime("%H_%M_%S")
    filename = f"history_text_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(history_text)
    print(filename)
    print("=" * 80)

    urls = re.findall(r"https?://[^\s<>\"{}|\\^`\[\]]+", history_text)
    candidates = [u for u in urls if not is_excluded(u) and not u.startswith("https://www.google.")]
    if candidates:
        print(f"\nCompany website found: {candidates[0]}")
        return candidates[0]

    print("\nNo official website URL extracted. Returning raw agent output.")
    return history_text


def _main() -> None:
    try:
        company_name = os.environ.get("TEST_COMPANY_NAME", "Data Origin SL")
        result = asyncio.run(search_company_website(company_name))
        public_ip = get_public_ip()
        print(f"\n{'='*80}")
        print(f"FINAL RESULT FOR {company_name}:")
        print(f"{'='*80}")
        print(result)
        print(f"{'='*80}")
        print(f"\nPublic IP Address: {public_ip}")
        print(f"{'='*80}")
    except Exception as exc:
        print(f"Error: {exc}")
        import traceback
        traceback.print_exc()
        print("\nEnsure you have:")
        print("1. Installed dependencies: pip install -r requirements.txt")
        print("2. Set BROWSER_USE_API_KEY in your environment or config.env (Browser-Use Cloud)")


if __name__ == "__main__":
    _main()


