"""
Extractor de stack tecnológico desde LinkedIn y Portfolio usando browser-use
"""
from browser_use import Agent, Browser, ChatBrowserUse, Tools
import asyncio
from typing import List, Dict, Optional
import json
import re
import sys
from pathlib import Path

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent))

from auth.linkedin_auth import LinkedInAuth
from auth.google_auth import GoogleAuth


class StackExtractor:
    """Extractor inteligente de stack tecnológico"""

    # Tecnologías comunes agrupadas por categorías
    TECH_KEYWORDS = {
        "languages": [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go",
            "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "SQL"
        ],
        "frameworks_backend": [
            "Django", "Flask", "FastAPI", "Node.js", "Express", "NestJS",
            "Spring", "Spring Boot", ".NET", "ASP.NET", "Rails", "Laravel"
        ],
        "frameworks_frontend": [
            "React", "Vue.js", "Angular", "Svelte", "Next.js", "Nuxt.js",
            "jQuery", "Bootstrap", "Tailwind CSS", "Material-UI"
        ],
        "databases": [
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
            "SQLite", "Oracle", "SQL Server", "Cassandra", "DynamoDB"
        ],
        "cloud_devops": [
            "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
            "Terraform", "Ansible", "Jenkins", "GitLab CI", "GitHub Actions",
            "CircleCI", "Travis CI"
        ],
        "ai_ml": [
            "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "Pandas",
            "NumPy", "OpenAI", "LangChain", "Hugging Face", "NLTK", "spaCy"
        ],
        "tools": [
            "Git", "Jira", "Confluence", "Slack", "Postman", "VSCode",
            "IntelliJ", "Figma", "Notion"
        ]
    }

    def __init__(self):
        self.tools = Tools()
        self._setup_tools()

    def _setup_tools(self):
        """Configura herramientas personalizadas para browser-use"""

        @self.tools.action('Guarda el stack tecnológico extraído')
        def save_stack(technologies: List[str]) -> str:
            """Guarda tecnologías extraídas"""
            self.extracted_stack = list(set(technologies))  # Eliminar duplicados
            return f"✅ Stack guardado: {len(self.extracted_stack)} tecnologías"

    async def extract_from_linkedin(self, linkedin_url: str, use_auth: bool = True) -> List[str]:
        """
        Extrae stack tecnológico desde perfil de LinkedIn

        Args:
            linkedin_url: URL del perfil de LinkedIn
            use_auth: Si True, intenta usar sesión guardada

        Returns:
            Lista de tecnologías detectadas
        """
        # Verificar si hay sesión autenticada
        linkedin_auth = LinkedInAuth()

        if use_auth and not linkedin_auth.has_valid_session():
            print("⚠️  No hay sesión autenticada de LinkedIn")
            print("💡 Ejecuta el login manual primero desde la interfaz o con:")
            print("   uv run python src/auth/linkedin_auth.py")
            return []

        llm = ChatBrowserUse()
        browser = Browser()

        # Si tenemos sesión, cargar cookies
        if use_auth and linkedin_auth.has_valid_session():
            try:
                cookies = linkedin_auth.get_session_cookies()
                if cookies:
                    print(f"🔐 Cargando sesión autenticada ({len(cookies)} cookies)...")
                    # Primero navegar a LinkedIn
                    page = await browser.get_current_page()

                    if page is None:
                        # Crear página si no existe
                        if hasattr(browser, 'browser') and browser.browser:
                            context = await browser.browser.new_context()
                            page = await context.new_page()

                    if page:
                        await page.goto("https://www.linkedin.com")
                        # Agregar cookies
                        context = page.context
                        await context.add_cookies(cookies)
                        print("✅ Sesión cargada")
            except Exception as e:
                print(f"⚠️  Error cargando sesión: {e}")

        task = f"""
        1. Ve a este perfil de LinkedIn: {linkedin_url}
        2. Navega por el perfil y extrae TODAS las tecnologías mencionadas en:
           - Experiencia laboral (títulos, descripciones de puestos)
           - Habilidades (Skills section)
           - Certificaciones
           - Proyectos
           - Resumen/About
        3. Busca específicamente: lenguajes de programación, frameworks, bases de datos,
           herramientas cloud/DevOps, tecnologías de IA/ML
        4. Organiza las tecnologías en una lista limpia (sin duplicados)
        5. Usa la función save_stack para guardar el resultado

        IMPORTANTE: Solo extrae nombres de tecnologías reales, no conceptos genéricos.
        Ejemplos correctos: "Python", "React", "AWS", "Docker", "PostgreSQL"
        Ejemplos incorrectos: "programming", "development", "agile"
        """

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            use_vision=True,
            tools=self.tools,
            save_conversation_path="logs/linkedin_stack_extraction.json"
        )

        try:
            print(f"🔍 Extrayendo stack desde LinkedIn: {linkedin_url}")
            await agent.run()
            return getattr(self, 'extracted_stack', [])
        except Exception as e:
            print(f"❌ Error extrayendo desde LinkedIn: {e}")
            return []

    async def extract_from_portfolio(self, portfolio_url: str, use_auth: bool = True) -> List[str]:
        """
        Extrae stack tecnológico desde portfolio personal

        Args:
            portfolio_url: URL del portfolio
            use_auth: Si True y es Google Drive, usa sesión guardada

        Returns:
            Lista de tecnologías detectadas
        """
        # Si es Google Drive, verificar autenticación
        is_google = "drive.google.com" in portfolio_url or "docs.google.com" in portfolio_url

        if is_google and use_auth:
            google_auth = GoogleAuth()
            if not google_auth.has_valid_session():
                print("⚠️  No hay sesión autenticada de Google")
                print("💡 Ejecuta el login manual primero desde la interfaz o con:")
                print("   uv run python src/auth/google_auth.py")
                return []

        llm = ChatBrowserUse()
        browser = Browser()

        # Si es Google y tenemos sesión, cargar cookies
        if is_google and use_auth:
            google_auth = GoogleAuth()
            if google_auth.has_valid_session():
                try:
                    cookies = google_auth.get_session_cookies()
                    if cookies:
                        print(f"🔐 Cargando sesión de Google ({len(cookies)} cookies)...")
                        page = await browser.get_current_page()

                        if page is None:
                            # Crear página si no existe
                            if hasattr(browser, 'browser') and browser.browser:
                                context = await browser.browser.new_context()
                                page = await context.new_page()

                        if page:
                            await page.goto("https://accounts.google.com")
                            context = page.context
                            await context.add_cookies(cookies)
                            print("✅ Sesión de Google cargada")
                except Exception as e:
                    print(f"⚠️  Error cargando sesión de Google: {e}")

        task = f"""
        1. Ve a este portfolio: {portfolio_url}
        2. Navega por TODO el sitio y extrae tecnologías mencionadas en:
           - Secciones de "About", "Skills", "Tech Stack"
           - Descripción de proyectos
           - Footer o header (a veces listan tecnologías)
           - Secciones de experiencia
        3. Busca logos de tecnologías, badges, iconos
        4. Lee código embebido o snippets si los hay
        5. Organiza las tecnologías en una lista limpia
        6. Usa la función save_stack para guardar el resultado

        IMPORTANTE: Extrae SOLO nombres de tecnologías específicas.
        """

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            use_vision=True,  # Crucial para detectar logos/badges
            tools=self.tools,
            save_conversation_path="logs/portfolio_stack_extraction.json"
        )

        try:
            print(f"🔍 Extrayendo stack desde Portfolio: {portfolio_url}")
            await agent.run()
            return getattr(self, 'extracted_stack', [])
        except Exception as e:
            print(f"❌ Error extrayendo desde Portfolio: {e}")
            return []

    async def extract_combined(
        self,
        linkedin_url: Optional[str] = None,
        portfolio_url: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Extrae stack de múltiples fuentes y combina resultados

        Args:
            linkedin_url: URL de LinkedIn (opcional)
            portfolio_url: URL de portfolio (opcional)

        Returns:
            Diccionario con tecnologías categorizadas y deduplicadas
        """
        all_technologies = []

        # Extraer de LinkedIn si se proporciona
        if linkedin_url:
            linkedin_stack = await self.extract_from_linkedin(linkedin_url)
            all_technologies.extend(linkedin_stack)

        # Extraer de Portfolio si se proporciona
        if portfolio_url:
            portfolio_stack = await self.extract_from_portfolio(portfolio_url)
            all_technologies.extend(portfolio_stack)

        # Deduplicar y normalizar
        unique_tech = list(set(all_technologies))

        # Categorizar tecnologías
        categorized = self._categorize_technologies(unique_tech)

        return {
            "all": sorted(unique_tech),
            "categorized": categorized,
            "count": len(unique_tech)
        }

    def _categorize_technologies(self, technologies: List[str]) -> Dict[str, List[str]]:
        """
        Categoriza tecnologías según tipo

        Args:
            technologies: Lista de tecnologías

        Returns:
            Diccionario con tecnologías categorizadas
        """
        categorized = {
            "languages": [],
            "frameworks_backend": [],
            "frameworks_frontend": [],
            "databases": [],
            "cloud_devops": [],
            "ai_ml": [],
            "tools": [],
            "other": []
        }

        for tech in technologies:
            tech_lower = tech.lower()
            categorized_flag = False

            for category, keywords in self.TECH_KEYWORDS.items():
                if any(tech_lower == keyword.lower() for keyword in keywords):
                    categorized[category].append(tech)
                    categorized_flag = True
                    break

            if not categorized_flag:
                categorized["other"].append(tech)

        return categorized

    @staticmethod
    def manual_extract_from_text(text: str) -> List[str]:
        """
        Extracción simple basada en keywords (fallback sin browser-use)

        Args:
            text: Texto del que extraer tecnologías

        Returns:
            Lista de tecnologías encontradas
        """
        extractor = StackExtractor()
        found_tech = []

        for category, keywords in extractor.TECH_KEYWORDS.items():
            for keyword in keywords:
                # Búsqueda case-insensitive
                pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                if pattern.search(text):
                    found_tech.append(keyword)

        return list(set(found_tech))


# Función de utilidad para pruebas rápidas
async def test_extraction():
    """Test básico del extractor"""
    extractor = StackExtractor()

    # Ejemplo con texto manual
    sample_text = """
    I'm a Full Stack Developer with 5 years of experience in Python, JavaScript,
    and TypeScript. I work with React, Node.js, and Django. Experienced with AWS,
    Docker, and Kubernetes. Databases: PostgreSQL, MongoDB, Redis.
    """

    print("=== Extracción manual desde texto ===")
    manual_stack = StackExtractor.manual_extract_from_text(sample_text)
    print(f"Tecnologías encontradas: {manual_stack}")

    # Ejemplo con URLs reales (descomenta para probar)
    # result = await extractor.extract_combined(
    #     linkedin_url="https://www.linkedin.com/in/tu-perfil",
    #     portfolio_url="https://tu-portfolio.com"
    # )
    # print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(test_extraction())
