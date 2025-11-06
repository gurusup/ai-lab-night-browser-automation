"""
Scraper de RemoteOK usando browser-use
"""
from browser_use import Agent, Browser, ChatBrowserUse, Tools
import asyncio
import json
from typing import List, Dict, Optional


class RemoteOKScraper:
    """Scraper inteligente para RemoteOK"""

    def __init__(self):
        self.tools = Tools()
        self._setup_tools()
        self.scraped_jobs = []

    def _setup_tools(self):
        """Configura herramientas personalizadas"""

        @self.tools.action('Guarda las ofertas de RemoteOK en formato JSON')
        def guardar_ofertas(jobs_json: str) -> str:
            """
            Guarda ofertas extraídas

            Args:
                jobs_json: JSON string con la lista de ofertas
            """
            try:
                jobs = json.loads(jobs_json) if isinstance(jobs_json, str) else jobs_json
                self.scraped_jobs = jobs
                with open('src/data/remoteok_jobs.json', 'w', encoding='utf-8') as f:
                    json.dump(jobs, f, indent=2, ensure_ascii=False)
                return f"✅ Guardadas {len(jobs)} ofertas de RemoteOK"
            except Exception as e:
                return f"❌ Error guardando ofertas: {e}"

    async def scrape(
        self,
        search_query: str,
        max_results: int = 10,
        location_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Scraper principal de RemoteOK

        Args:
            search_query: Búsqueda (ej: "Python")
            max_results: Número máximo de resultados
            location_filter: Filtro de ubicación opcional (ej: "Europe", "Spain")

        Returns:
            Lista de ofertas
        """
        llm = ChatBrowserUse()
        browser = Browser()

        # Construir URL con query
        base_url = "https://remoteok.com"
        search_url = f"{base_url}/remote-jobs?q={search_query.replace(' ', '+')}"

        location_text = ""
        if location_filter:
            location_text = f"Intenta filtrar solo ofertas que mencionen: {location_filter}"

        task = f"""
        1. Ve a RemoteOK: {search_url}
        2. {location_text}
        3. Extrae información de las primeras {max_results} ofertas:
           - Título del puesto (title)
           - Empresa (company)
           - Ubicación permitida (location) - puede ser "Worldwide", "Europe", etc
           - Tags de tecnologías (tags) - lista de tecnologías mencionadas
           - Salario si está visible (salary)
           - URL directa a la oferta (url) - debe ser la URL completa de RemoteOK
           - Descripción corta (description) - primeras 2-3 líneas de la descripción
        4. Organiza los datos en una lista de diccionarios JSON con las claves indicadas
        5. Convierte la lista a un JSON string
        6. Llama a guardar_ofertas pasando el JSON string como parámetro jobs_json

        IMPORTANTE:
        - RemoteOK muestra trabajos 100% remotos
        - Muchas ofertas tienen tags de tecnologías visibles, extráelos
        - Si aparecen modales o anuncios, ciérralos
        - Las URLs deben ser completas: https://remoteok.com/remote-jobs/...
        - Si no encuentras algún campo (como salary), déjalo como null
        - Los tags suelen aparecer como badges/pills con nombres de tecnologías
        - El parámetro jobs_json debe ser un string JSON, no un objeto
        """

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            use_vision=True,
            tools=self.tools,
            save_conversation_path="logs/remoteok_conversation.json"
        )

        try:
            print(f"🚀 Iniciando scraping de RemoteOK: '{search_query}'")
            await agent.run()
            print(f"✅ RemoteOK scraping completado! {len(self.scraped_jobs)} ofertas")
            return self.scraped_jobs
        except Exception as error:
            print(f"❌ Error durante scraping de RemoteOK: {error}")
            return []


async def scrape_remoteok_jobs(
    search_query: str,
    max_results: int = 10,
    location_filter: Optional[str] = None
):
    """Función helper para ejecutar el scraper"""
    scraper = RemoteOKScraper()
    return await scraper.scrape(
        search_query=search_query,
        max_results=max_results,
        location_filter=location_filter
    )


if __name__ == "__main__":
    # Test del scraper
    asyncio.run(scrape_remoteok_jobs(
        search_query="Python",
        max_results=10,
        location_filter="Europe"
    ))
