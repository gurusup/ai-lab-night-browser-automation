"""
Extractor de información de GitHub
"""
import requests
from typing import Dict, List, Optional
import re


class GitHubExtractor:
    """Extrae información de perfiles de GitHub"""

    def __init__(self):
        self.base_url = "https://api.github.com"

    def extract_from_username(self, username: str) -> Dict:
        """
        Extrae información desde un username de GitHub

        Args:
            username: Username de GitHub

        Returns:
            Diccionario con información del perfil
        """
        try:
            # Obtener info del usuario
            user_info = self._get_user_info(username)

            # Obtener repositorios
            repos = self._get_repositories(username)

            # Analizar lenguajes y tecnologías
            tech_stack = self._analyze_technologies(repos)

            return {
                "name": user_info.get("name"),
                "bio": user_info.get("bio"),
                "location": user_info.get("location"),
                "company": user_info.get("company"),
                "blog": user_info.get("blog"),
                "public_repos": user_info.get("public_repos", 0),
                "followers": user_info.get("followers", 0),
                "technologies": tech_stack["technologies"],
                "top_languages": tech_stack["languages"],
                "notable_projects": self._get_notable_projects(repos),
                "profile_url": f"https://github.com/{username}"
            }
        except Exception as e:
            print(f"❌ Error extrayendo GitHub: {e}")
            return {}

    def extract_from_url(self, github_url: str) -> Dict:
        """
        Extrae información desde una URL de GitHub

        Args:
            github_url: URL del perfil de GitHub

        Returns:
            Diccionario con información del perfil
        """
        # Extraer username de la URL
        match = re.search(r'github\.com/([^/]+)', github_url)
        if match:
            username = match.group(1)
            return self.extract_from_username(username)
        else:
            raise ValueError("URL de GitHub inválida")

    def _get_user_info(self, username: str) -> Dict:
        """Obtiene información básica del usuario"""
        url = f"{self.base_url}/users/{username}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    def _get_repositories(self, username: str, max_repos: int = 30) -> List[Dict]:
        """Obtiene repositorios del usuario"""
        url = f"{self.base_url}/users/{username}/repos"
        params = {
            "sort": "updated",
            "per_page": max_repos
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def _analyze_technologies(self, repos: List[Dict]) -> Dict:
        """Analiza tecnologías usadas en los repositorios"""
        languages = {}
        technologies = set()

        for repo in repos:
            # Contar lenguajes
            if repo.get("language"):
                lang = repo["language"]
                languages[lang] = languages.get(lang, 0) + 1

            # Detectar tecnologías por nombre de repo y descripción
            repo_text = f"{repo.get('name', '')} {repo.get('description', '')}".lower()

            # Frameworks comunes
            tech_keywords = {
                "React", "Vue", "Angular", "Django", "Flask", "FastAPI",
                "Docker", "Kubernetes", "AWS", "Azure", "GCP",
                "PostgreSQL", "MongoDB", "Redis", "TensorFlow", "PyTorch",
                "Node.js", "Express", "Next.js", "GraphQL", "REST API"
            }

            for tech in tech_keywords:
                if tech.lower() in repo_text:
                    technologies.add(tech)

        # Ordenar lenguajes por frecuencia
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)

        return {
            "languages": [lang for lang, _ in sorted_languages[:10]],
            "technologies": list(technologies)
        }

    def _get_notable_projects(self, repos: List[Dict], max_projects: int = 5) -> List[Dict]:
        """Obtiene proyectos más notables"""
        # Ordenar por stars
        sorted_repos = sorted(
            repos,
            key=lambda x: x.get("stargazers_count", 0),
            reverse=True
        )

        notable = []
        for repo in sorted_repos[:max_projects]:
            if not repo.get("fork"):  # Excluir forks
                notable.append({
                    "name": repo["name"],
                    "description": repo.get("description", ""),
                    "language": repo.get("language", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "url": repo["html_url"]
                })

        return notable


# Función helper
def extract_github_profile(github_url: str) -> Dict:
    """
    Extrae perfil de GitHub desde una URL

    Args:
        github_url: URL del perfil de GitHub

    Returns:
        Diccionario con información del perfil
    """
    extractor = GitHubExtractor()
    return extractor.extract_from_url(github_url)


if __name__ == "__main__":
    # Test con un perfil de ejemplo
    test_username = "torvalds"  # Linus Torvalds como ejemplo

    extractor = GitHubExtractor()
    profile = extractor.extract_from_username(test_username)

    print("=== Perfil de GitHub ===")
    print(f"Nombre: {profile.get('name')}")
    print(f"Bio: {profile.get('bio')}")
    print(f"Ubicación: {profile.get('location')}")
    print(f"Repos públicos: {profile.get('public_repos')}")
    print(f"Seguidores: {profile.get('followers')}")
    print(f"\nLenguajes principales: {', '.join(profile.get('top_languages', []))}")
    print(f"Tecnologías: {', '.join(profile.get('technologies', []))}")
    print(f"\nProyectos notables:")
    for proj in profile.get('notable_projects', [])[:3]:
        print(f"  - {proj['name']} ({proj['stars']} ⭐): {proj['description']}")
