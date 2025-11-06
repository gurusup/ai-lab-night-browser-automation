"""
Scraper mejorado de LinkedIn usando browser-use - Compatible con nueva arquitectura
"""
from browser_use import Agent, Browser, ChatBrowserUse, Tools
import asyncio
import json
from typing import List, Dict, Optional


class LinkedInScraper:
    """Scraper inteligente para LinkedIn Jobs"""

    def __init__(self):
        self.tools = Tools()
        self._setup_tools()
        self.scraped_jobs = []

    def _setup_tools(self):
        """Configura herramientas personalizadas"""

        @self.tools.action('Guarda las ofertas de LinkedIn en formato JSON')
        def guardar_ofertas(jobs_json: str) -> str:
            """
            Guarda ofertas extraídas

            Args:
                jobs_json: JSON string con la lista de ofertas
            """
            try:
                jobs = json.loads(jobs_json) if isinstance(jobs_json, str) else jobs_json
                self.scraped_jobs = jobs
                with open('src/data/linkedin_jobs.json', 'w', encoding='utf-8') as f:
                    json.dump(jobs, f, indent=2, ensure_ascii=False)
                return f"✅ Guardadas {len(jobs)} ofertas de LinkedIn"
            except Exception as e:
                return f"❌ Error guardando ofertas: {e}"

    async def scrape(
        self,
        search_query: str,
        location: str = "Spain",
        max_results: int = 10,
        remote_only: bool = True,
        published_within_days: int = 7
    ) -> List[Dict]:
        """
        Scraper principal de LinkedIn

        Args:
            search_query: Búsqueda (ej: "Python developer")
            location: Ubicación
            max_results: Número máximo de resultados
            remote_only: Solo trabajos remotos
            published_within_days: Ofertas publicadas en los últimos N días

        Returns:
            Lista de ofertas
        """
        llm = ChatBrowserUse()
        browser = Browser()

        # Construir filtros dinámicamente
        filters = []
        if published_within_days <= 1:
            filters.append("publicado últimas 24 horas")
        elif published_within_days <= 7:
            filters.append("publicado última semana")
        else:
            filters.append("publicado último mes")

        if remote_only:
            filters.append("trabajo remoto")

        filters_text = f"Aplica filtros: {', '.join(filters)}"

        task = f"""
        1. Ve a LinkedIn Jobs: https://www.linkedin.com/jobs
        2. Busca: "{search_query}" en ubicación "{location}"
        3. {filters_text}
        4. Extrae información de las primeras {max_results} ofertas:
           - Título del puesto (title)
           - Empresa (company)
           - Ubicación (location)
           - Nivel (level) si está visible (ej: "Mid-Senior", "Entry level")
           - Tipo de empleo (employment_type) si visible (ej: "Full-time", "Contract")
           - URL directa a la oferta (url)
           - Descripción corta (description) - primeras 2-3 líneas
        5. Organiza los datos en una lista de diccionarios JSON con las claves indicadas
        6. Convierte la lista a un JSON string
        7. Llama a guardar_ofertas pasando el JSON string como parámetro jobs_json

        IMPORTANTE:
        - Si LinkedIn pide login, intenta acceder a trabajos públicos sin iniciar sesión
        - Si aparecen modales, ciérralos
        - Extrae solo ofertas reales
        - Si no encuentras algún campo (como level), déjalo como null
        - El parámetro jobs_json debe ser un string JSON, no un objeto
        """

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            use_vision=True,
            tools=self.tools,
            save_conversation_path="logs/linkedin_conversation.json"
        )

        try:
            print(f"🚀 Iniciando scraping de LinkedIn: '{search_query}' en {location}")
            await agent.run()
            print(f"✅ LinkedIn scraping completado! {len(self.scraped_jobs)} ofertas")
            return self.scraped_jobs
        except Exception as error:
            print(f"❌ Error durante scraping de LinkedIn: {error}")
            return []


async def scrape_linkedin_jobs(
    search_query: str,
    location: str = "Spain",
    max_results: int = 10,
    remote_only: bool = True
):
    """Función helper para ejecutar el scraper"""
    scraper = LinkedInScraper()
    return await scraper.scrape(
        search_query=search_query,
        location=location,
        max_results=max_results,
        remote_only=remote_only
    )


if __name__ == "__main__":
    # Test del scraper
    asyncio.run(scrape_linkedin_jobs(
        search_query="Python developer",
        location="Spain",
        max_results=10
    ))
