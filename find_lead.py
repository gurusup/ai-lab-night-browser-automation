from browser_use import Agent, Browser, ChatBrowserUse
import asyncio

async def find_coordinator():
    # === Configuración del navegador ===
    browser = Browser(
        use_cloud=True,     # mejora estabilidad (usa navegador en la nube)
        headless=True        # sin ventana visible
    )

    llm = ChatBrowserUse()

    # === Cambia estos datos según el proyecto que quieras investigar ===
    project_title = "Revealing the Epigenetic Regulatory Network with Single-Molecule Precision"
    project_acronym = "SM-Epigen"
    project_link = "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/projects-details/31045243/801655/H2020"

    # === Prompt principal ===
    search_prompt = f"""
    You are an expert in research intelligence and collaboration mapping.

    Your task is to identify the coordinator and potential lead contact
    for the following EU-funded research project.

    Project title: "{project_title}"
    Acronym: "{project_acronym}"
    Project link: {project_link}

    Follow these steps:
    1. Visit the project page on the provided link.
       - Extract the coordinator institution name and country.
       - If a person or contact email appears, capture it.
    2. If no personal contact is listed, open a new tab and search on Google for:
       - "{project_acronym}" + "project coordinator"
       - "{project_acronym}" + "principal investigator"
       - "{project_acronym}" + "functional genomics" + "cancer" + "contact"
    3. From the first 5–10 results, extract:
       - Coordinator organization
       - Lead researcher (if found)
       - Contact email or institutional webpage (if available)
       - Source URL
       - Short reasoning why this is likely the correct contact
    4. Return the output clearly in plain text, with this structure:

    ---
    Project: {project_title}
    Coordinator organization: [name]
    Lead contact: [name, position, email or profile link]
    Source: [URL]
    Reasoning: [why this person or institution is relevant]
    ---
    """

    # === Crear el agente ===
    agent = Agent(
        task=search_prompt,
        llm=llm,
        browser=browser,
    )

    # === Ejecutar ===
    history = await agent.run()

    # === Extraer salida final ===
    if isinstance(history, list) and len(history) > 0:
        final_output = history[-1].get("content", "")
    else:
        final_output = str(history)

    # === Guardar resultados ===
    with open("coordinator_search.txt", "w", encoding="utf-8") as f:
        f.write(final_output)

    print("✅ Results saved to coordinator_search.txt")

if __name__ == "__main__":
    asyncio.run(find_coordinator())

