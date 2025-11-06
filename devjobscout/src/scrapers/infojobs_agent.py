"""
Scraper de InfoJobs usando browser-use
"""
from browser_use import Agent, Browser, ChatBrowserUse, Tools
import asyncio
import json
from typing import List, Dict, Optional


class InfoJobsScraper:
    """Scraper inteligente para InfoJobs"""

    def __init__(self):
        self.tools = Tools()
        self._setup_tools()
        self.scraped_jobs = []

    def _setup_tools(self):
        """Configura herramientas personalizadas"""

        @self.tools.action('Guarda las ofertas de InfoJobs en formato JSON')
        def guardar_ofertas(jobs_json: str) -> str:
            """
            Guarda ofertas extraídas

            Args:
                jobs_json: JSON string con la lista de ofertas
            """
            try:
                jobs = json.loads(jobs_json) if isinstance(jobs_json, str) else jobs_json
                self.scraped_jobs = jobs
                with open('src/data/infojobs_jobs.json', 'w', encoding='utf-8') as f:
                    json.dump(jobs, f, indent=2, ensure_ascii=False)
                return f"✅ Guardadas {len(jobs)} ofertas de InfoJobs"
            except Exception as e:
                return f"❌ Error guardando ofertas: {e}"

    async def scrape(
        self,
        search_query: str,
        location: str = "España",
        max_results: int = 10,
        remote_only: bool = True
    ) -> List[Dict]:
        """
        Scraper principal de InfoJobs

        Args:
            search_query: Búsqueda (ej: "Python developer")
            location: Ubicación
            max_results: Número máximo de resultados
            remote_only: Solo trabajos remotos

        Returns:
            Lista de ofertas
        """
        llm = ChatBrowserUse()
        browser = Browser()

        # Construir tarea dinámica
        filters = []
        if remote_only:
            filters.append("trabajo remoto o teletrabajo")

        filters_text = f"Aplica filtros: {', '.join(filters)}" if filters else ""

        task = f"""
        1. Ve a InfoJobs España: https://www.infojobs.net/
        2. Busca: "{search_query}" en "{location}"
        3. {filters_text}
        4. Extrae información de las primeras {max_results} ofertas:
           - Título del puesto (title)
           - Empresa (company)
           - Ubicación (location)
           - Tipo de contrato si está visible (contract_type)
           - Salario si está visible (salary)
           - URL directa a la oferta (url)
           - Descripción corta (description) - primeras 2-3 líneas
        5. Organiza los datos en una lista de diccionarios JSON con las claves indicadas
        6. Convierte la lista a un JSON string
        7. Llama a guardar_ofertas pasando el JSON string como parámetro jobs_json

        IMPORTANTE:
        - Si InfoJobs pide login o registro, intenta continuar sin registrarte
        - Si aparecen modales de cookies, acéptalos
        - Extrae solo ofertas reales, no anuncios
        - Si no encuentras algún campo (como salary), déjalo como null
        - El parámetro jobs_json debe ser un string JSON, no un objeto
        """

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            use_vision=True,
            tools=self.tools,
            save_conversation_path="logs/infojobs_conversation.json"
        )

        try:
            print(f"🚀 Iniciando scraping de InfoJobs: '{search_query}' en {location}")
            await agent.run()
            print(f"✅ InfoJobs scraping completado! {len(self.scraped_jobs)} ofertas")
            return self.scraped_jobs
        except Exception as error:
            print(f"❌ Error durante scraping de InfoJobs: {error}")
            return []


async def scrape_infojobs_jobs(
    search_query: str,
    location: str = "España",
    max_results: int = 10
):
    """Función helper para ejecutar el scraper"""
    scraper = InfoJobsScraper()
    return await scraper.scrape(
        search_query=search_query,
        location=location,
        max_results=max_results,
        remote_only=True
    )


if __name__ == "__main__":
    # Test del scraper
    asyncio.run(scrape_infojobs_jobs(
        search_query="Python developer",
        location="España",
        max_results=10
    ))
