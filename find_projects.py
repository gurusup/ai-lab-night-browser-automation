from browser_use import Agent, Browser, ChatBrowserUse
import asyncio

async def example():
    browser = Browser(use_cloud=True, headless=True)  # no abre ventana
    llm = ChatBrowserUse()

    # ---- PROMPT: buscar proyectos similares ----
    search_prompt = """
You are an expert in EU research and innovation project analysis.
Your goal is to identify past EU-funded projects similar to a new topic.

1. Go to: https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/projects-results
2. Use ONLY the search bar INSIDE the "Projects & Results" section (ignore the global search at the top of the page).
3. Type this query carefully: "broad spectrum antiviral small molecule" and press enter.
4. Wait until the list of project cards is fully visible. Wait at least 10 seconds after the results appear to ensure Angular has finished rendering.
5. Scroll slowly down to the bottom of the page and capture at least the first 20 projects.
6. For each project, extract the following fields:
   - Project title
   - Acronym
   - Programme (e.g., Horizon 2020, Horizon Europe, EU4Health)
   - Short summary or objective
   - Link to the project page
7. After extraction, analyze which projects are thematically related to the topic:
   “Development of novel broad spectrum small molecule antiviral therapeutics for pathogens with epidemic potential.”
8. Keep only the 6 most thematically relevant projects. For each, provide:
   - Title and Acronym
   - Programme
   - Summary
   - Project link
   - One-sentence reasoning for its relevance.
9. Write the results to a local file named "relevant_projects.txt" in clean Markdown format.

Important:
- Avoid using the global search input at the top (it is inside a shadowRoot).
- If any part of the site fails to load, refresh once and retry.
- Wait for all asynchronous content (XHRs) before extraction.
- Keep reasoning concise but analytical.
- Output only the extracted list and reasoning, no debug or meta information.
"""

    agent = Agent(
        task=search_prompt,
        llm=llm,
        browser=browser,
    )

    # Ejecutar el agente
    history = await agent.run()

    # Extraer solo el resultado final (último mensaje)
    if isinstance(history, list) and len(history) > 0:
        final_output = history[-1].get("content", "")
    else:
        final_output = str(history)

    # Guardar en un archivo de texto
    with open("results.txt", "w", encoding="utf-8") as f:
        f.write(final_output)

    print("✅ Results saved to results.txt")

if __name__ == "__main__":
    asyncio.run(example())

