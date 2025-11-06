from browser_use import Agent, Browser, ChatBrowserUse, Tools
import asyncio
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear tool controller
tools = Tools()

# Custom tool para guardar los datos de las ofertas
@tools.action('Guarda las ofertas de trabajo extraídas en formato JSON. El parámetro jobs debe ser una lista de diccionarios con los datos de cada oferta.')
def guardar_ofertas(jobs: list) -> str:
    """Guarda las ofertas de trabajo en JSON"""
    with open('src/data/linkedin_jobs.json', 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    return f"✅ Guardadas {len(jobs)} ofertas en linkedin_jobs.json"

async def scrape_linkedin_jobs():
    """Scraper de LinkedIn Jobs usando browser-use"""

    # Inicializar LLM y Browser
    llm = ChatBrowserUse()
    browser = Browser()

    # Crear agente con instrucciones
    agent = Agent(
        task="""
        1. Ve a LinkedIn Jobs (https://www.linkedin.com/jobs)
        2. Busca: "Node.js developer remote Spain"
        3. Aplica filtros: publicado última semana, trabajo remoto
        4. Extrae de las primeras 10 ofertas:
           - Título del puesto
           - Empresa
           - Ubicación
           - Link directo a la oferta
           - Descripción corta (primeras 2-3 líneas)
        5. Organiza los datos en una lista de diccionarios con las claves:
           title, company, location, url, description
        6. Usa la función guardar_ofertas para guardar los resultados
        """,
        llm=llm,
        browser=browser,
        use_vision=True,  # Usa visión para entender mejor la página
        tools=tools,
        save_conversation_path="logs/linkedin_conversation.json"
    )

    try:
        print("🚀 Iniciando scraping de LinkedIn...")
        result = await agent.run()
        print("✅ Scraping completado!")
        return result
    except Exception as error:
        print(f"❌ Error durante scraping: {error}")
        raise
    # Note: browser-use Agent cierra el browser automáticamente

if __name__ == "__main__":
    # Test rápido
    asyncio.run(scrape_linkedin_jobs())
