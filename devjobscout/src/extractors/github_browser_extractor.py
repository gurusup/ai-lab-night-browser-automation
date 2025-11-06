"""
Extractor avanzado de GitHub usando browser-use
Navega por el perfil y extrae métricas profundas
"""
from browser_use import Agent, Browser, ChatBrowserUse, Tools
import asyncio
import json
from typing import Dict, List, Optional


class GitHubBrowserExtractor:
    """Extrae información completa de GitHub navegando con browser-use"""

    def __init__(self):
        self.tools = Tools()
        self._setup_tools()
        self.extracted_data = {}

    def _setup_tools(self):
        """Configura herramientas personalizadas"""

        @self.tools.action('Guarda la información extraída de GitHub')
        def guardar_github_info(
            name: str = "",
            username: str = "",
            bio: str = "",
            location: str = "",
            company: str = "",
            website: str = "",
            followers: int = 0,
            following: int = 0,
            public_repos: int = 0,
            contributions_last_year: int = 0,
            languages_json: str = "[]",
            repositories_json: str = "[]",
            frameworks_json: str = "[]",
            tools_json: str = "[]",
            specializations_json: str = "[]",
            activity_level: str = "Moderate"
        ) -> str:
            """
            Guarda información del perfil de GitHub con parámetros individuales.

            Args:
                name: Nombre completo
                username: Username de GitHub
                bio: Biografía
                location: Ubicación
                company: Empresa actual
                website: Sitio web/blog
                followers: Número de seguidores
                following: Número de following
                public_repos: Número de repositorios públicos
                contributions_last_year: Contribuciones en el último año
                languages_json: JSON string con lista de lenguajes y porcentajes
                repositories_json: JSON string con lista de repositorios destacados
                frameworks_json: JSON string con lista de frameworks
                tools_json: JSON string con lista de herramientas
                specializations_json: JSON string con especializaciones
                activity_level: Nivel de actividad (Very Active, Active, Moderate, Low)
            """
            try:
                # Parsear JSON strings
                languages = json.loads(languages_json) if languages_json else []
                repositories = json.loads(repositories_json) if repositories_json else []
                frameworks = json.loads(frameworks_json) if frameworks_json else []
                tools = json.loads(tools_json) if tools_json else []
                specializations = json.loads(specializations_json) if specializations_json else []

                # Construir estructura de datos
                data = {
                    "name": name,
                    "username": username,
                    "bio": bio,
                    "location": location,
                    "company": company if company else None,
                    "website": website,
                    "followers": followers,
                    "following": following,
                    "public_repos": public_repos,
                    "contributions_last_year": contributions_last_year,
                    "languages": languages,
                    "repositories": repositories,
                    "frameworks": frameworks,
                    "tools": tools,
                    "specializations": specializations,
                    "activity_level": activity_level,
                    "profile_url": f"https://github.com/{username}"
                }

                self.extracted_data = data

                # Guardar en archivo para debug
                with open('src/data/github_profile.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                return f"✅ Información de GitHub guardada correctamente: {name} (@{username})"
            except Exception as e:
                return f"❌ Error guardando info: {e}"

    async def extract_profile(self, github_url: str) -> Dict:
        """
        Extrae perfil completo de GitHub navegando con browser-use

        Args:
            github_url: URL del perfil (ej: https://github.com/usuario)

        Returns:
            Dict con toda la información extraída
        """
        llm = ChatBrowserUse()
        browser = Browser()

        task = f"""
        Ve a {github_url} y extrae toda la información visible del perfil de GitHub.

        PASO 1: NAVEGAR Y EXTRAER
        ==========================

        Extrae la siguiente información del perfil:

        **Información básica:**
        - Nombre completo
        - Username
        - Bio/descripción
        - Ubicación
        - Empresa actual (si visible)
        - Website/blog (si visible)
        - Número de seguidores
        - Número de following
        - Número de repositorios públicos

        **Estadísticas de contribución:**
        - Contribuciones totales en el último año (busca en el gráfico o stats)

        **Lenguajes principales:**
        Determina los lenguajes más usados (top 5-10) con sus porcentajes aproximados si están visibles.
        Formato de cada lenguaje: {{"language": "Python", "percentage": 45}}

        **Repositorios destacados:**
        Identifica los 3-5 repositorios más importantes (por estrellas si es visible, o los pinned).
        Para cada repo: nombre, descripción breve, lenguaje, estrellas (si visible), URL.
        Formato: {{"name": "repo-name", "description": "desc", "language": "Python", "stars": 10, "url": "..."}}

        **Habilidades técnicas inferidas:**
        Basándote en repositorios y descripción, infiere:
        - Frameworks: ["React", "Django", "Next.js"]
        - Herramientas: ["Docker", "Git", "AWS"]
        - Especializaciones: ["Backend", "DevOps"]

        **Nivel de actividad:**
        Clasifica como: "Very Active", "Active", "Moderate", o "Low"
        Basándote en contribuciones recientes y número de repos activos.

        PASO 2: GUARDAR LA INFORMACIÓN
        ===============================

        Una vez extraída toda la información, llama a la función guardar_github_info con estos parámetros:

        guardar_github_info(
            name="Nombre Completo",
            username="username",
            bio="Biografía del usuario",
            location="Ciudad, País",
            company="Empresa" (o "" si no visible),
            website="URL del sitio web" (o "" si no visible),
            followers=número_de_seguidores,
            following=número_de_following,
            public_repos=número_de_repos_públicos,
            contributions_last_year=número_de_contribuciones,
            languages_json='[{{"language": "Python", "percentage": 40}}, {{"language": "JavaScript", "percentage": 30}}]',
            repositories_json='[{{"name": "repo1", "description": "desc", "language": "Python", "stars": 10, "url": "..."}}]',
            frameworks_json='["React", "Django", "FastAPI"]',
            tools_json='["Docker", "Git", "AWS"]',
            specializations_json='["Backend", "DevOps"]',
            activity_level="Active"
        )

        IMPORTANTE:
        - Los parámetros languages_json, repositories_json, frameworks_json, tools_json, specializations_json
          DEBEN ser strings JSON válidos (entre comillas simples)
        - Extrae solo la información que sea VISIBLE en el perfil
        - Si algo no está visible, usa valores por defecto ("" para strings, 0 para números, [] para listas)
        - DEBES llamar a guardar_github_info al final para que se guarde la información
        """

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            use_vision=True,
            tools=self.tools,
            save_conversation_path="logs/github_browser_conversation.json"
        )

        try:
            print(f"🚀 Navegando por GitHub: {github_url}")
            await agent.run()
            print(f"✅ Extracción completa de GitHub!")
            return self.extracted_data
        except Exception as error:
            print(f"❌ Error durante extracción de GitHub: {error}")
            return {}


async def extract_github_profile_browser(github_url: str) -> Dict:
    """
    Helper function para extraer perfil de GitHub con browser-use

    Args:
        github_url: URL del perfil de GitHub

    Returns:
        Dict con toda la información extraída
    """
    extractor = GitHubBrowserExtractor()
    return await extractor.extract_profile(github_url)


if __name__ == "__main__":
    # Test
    import sys

    if len(sys.argv) > 1:
        github_url = sys.argv[1]
    else:
        github_url = "https://github.com/torvalds"  # Ejemplo

    print(f"=== Extrayendo perfil de {github_url} ===")
    result = asyncio.run(extract_github_profile_browser(github_url))

    print("\n=== Resultado ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
