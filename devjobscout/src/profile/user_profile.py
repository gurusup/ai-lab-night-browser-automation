"""
Gestión del perfil unificado del usuario
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class UserProfile:
    """Perfil completo del usuario combinando todas las fuentes"""

    # Información básica
    name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None

    # Stack tecnológico
    technologies: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)

    # Experiencia
    years_of_experience: Optional[int] = None
    current_role: Optional[str] = None
    companies: List[str] = field(default_factory=list)

    # Enlaces
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # Proyectos destacados
    notable_projects: List[Dict] = field(default_factory=list)

    # Preferencias de búsqueda
    desired_roles: List[str] = field(default_factory=list)
    work_preferences: Dict = field(default_factory=dict)

    # Fuentes de datos
    sources: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convierte el perfil a diccionario"""
        return {
            "name": self.name,
            "location": self.location,
            "bio": self.bio,
            "technologies": self.technologies,
            "languages": self.languages,
            "frameworks": self.frameworks,
            "tools": self.tools,
            "years_of_experience": self.years_of_experience,
            "current_role": self.current_role,
            "companies": self.companies,
            "linkedin_url": self.linkedin_url,
            "github_url": self.github_url,
            "portfolio_url": self.portfolio_url,
            "notable_projects": self.notable_projects,
            "desired_roles": self.desired_roles,
            "work_preferences": self.work_preferences,
            "sources": self.sources
        }

    def save(self, filepath: str = "src/data/user_profile.json"):
        """Guarda el perfil en un archivo JSON"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str = "src/data/user_profile.json") -> 'UserProfile':
        """Carga el perfil desde un archivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            profile = cls()
            for key, value in data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            return profile
        except FileNotFoundError:
            return cls()

    def generate_search_context(self) -> str:
        """
        Genera un contexto enriquecido para las búsquedas de empleo

        Returns:
            String con toda la información relevante del perfil
        """
        context_parts = []

        # === INFORMACIÓN BÁSICA ===
        context_parts.append("=== PERFIL DEL CANDIDATO ===")

        if self.name:
            context_parts.append(f"Nombre: {self.name}")

        if self.location:
            context_parts.append(f"Ubicación: {self.location}")

        if self.current_role:
            context_parts.append(f"Rol actual: {self.current_role}")

        if self.years_of_experience:
            context_parts.append(f"Años de experiencia: {self.years_of_experience}")

        if self.bio:
            context_parts.append(f"Bio: {self.bio}")

        context_parts.append("")  # Línea vacía

        # === STACK TECNOLÓGICO ===
        context_parts.append("=== STACK TECNOLÓGICO ===")

        if self.languages:
            lang_str = ", ".join(self.languages[:10])
            context_parts.append(f"Lenguajes: {lang_str}")

        if self.frameworks:
            fw_str = ", ".join(self.frameworks[:10])
            context_parts.append(f"Frameworks: {fw_str}")

        if self.technologies:
            tech_str = ", ".join(self.technologies[:15])
            context_parts.append(f"Tecnologías: {tech_str}")

        if self.tools:
            tools_str = ", ".join(self.tools[:10])
            context_parts.append(f"Herramientas: {tools_str}")

        context_parts.append("")

        # === EXPERIENCIA LABORAL ===
        if self.companies:
            context_parts.append("=== EXPERIENCIA LABORAL ===")
            companies_str = ", ".join(self.companies[:7])
            context_parts.append(f"Empresas: {companies_str}")
            context_parts.append("")

        # === PROYECTOS Y CONTRIBUCIONES ===
        if self.notable_projects:
            context_parts.append("=== PROYECTOS DESTACADOS ===")
            for i, project in enumerate(self.notable_projects[:5], 1):
                proj_name = project.get("name", "")
                proj_desc = project.get("description", "")
                proj_lang = project.get("language", "")
                stars = project.get("stars", 0)

                proj_info = f"{i}. {proj_name}"
                if proj_lang:
                    proj_info += f" ({proj_lang})"
                if stars:
                    proj_info += f" - {stars} estrellas"
                if proj_desc:
                    proj_info += f" - {proj_desc[:80]}"

                context_parts.append(proj_info)
            context_parts.append("")

        # === MÉTRICAS DE GITHUB ===
        if self.sources.get("github") and isinstance(self.sources["github"], dict):
            github_metrics = self.sources["github"]
            if github_metrics.get("status") == "loaded":
                context_parts.append("=== ACTIVIDAD EN GITHUB ===")

                if github_metrics.get("public_repos"):
                    context_parts.append(f"Repositorios públicos: {github_metrics['public_repos']}")

                if github_metrics.get("contributions_last_year"):
                    context_parts.append(f"Contribuciones último año: {github_metrics['contributions_last_year']}")

                if github_metrics.get("followers"):
                    context_parts.append(f"Seguidores: {github_metrics['followers']}")

                if github_metrics.get("activity_level"):
                    context_parts.append(f"Nivel de actividad: {github_metrics['activity_level']}")

                if github_metrics.get("specializations"):
                    specs = github_metrics["specializations"]
                    if specs:
                        context_parts.append(f"Especializaciones: {', '.join(specs)}")

                context_parts.append("")

        # === PREFERENCIAS ===
        if self.work_preferences or self.desired_roles:
            context_parts.append("=== PREFERENCIAS ===")

            if self.desired_roles:
                roles_str = ", ".join(self.desired_roles[:5])
                context_parts.append(f"Roles deseados: {roles_str}")

            if self.work_preferences:
                if self.work_preferences.get("remote"):
                    context_parts.append("Preferencia: Trabajo remoto")
                if self.work_preferences.get("location"):
                    context_parts.append(f"Ubicación preferida: {self.work_preferences['location']}")
                if self.work_preferences.get("salary_min"):
                    context_parts.append(f"Salario mínimo: {self.work_preferences['salary_min']}")

        return "\n".join(context_parts)

    def merge_from_cv(self, cv_data: Dict):
        """Integra datos extraídos del CV"""
        if cv_data.get("all"):
            self.technologies.extend(cv_data["all"])
            self.technologies = list(set(self.technologies))  # Deduplicar

        # Años de experiencia
        if cv_data.get("years_experience") and cv_data["years_experience"] > 0:
            self.years_of_experience = cv_data["years_experience"]

        # Roles
        if cv_data.get("roles"):
            if cv_data["roles"]:
                self.current_role = cv_data["roles"][0]  # Usar el primer rol como actual

        # Empresas
        if cv_data.get("companies"):
            self.companies.extend(cv_data["companies"])
            self.companies = list(set(self.companies))  # Deduplicar

        # Bio
        if cv_data.get("bio") and not self.bio:
            self.bio = cv_data["bio"]

        # Contact info
        if cv_data.get("contact"):
            contact = cv_data["contact"]
            if contact.get("linkedin") and not self.linkedin_url:
                self.linkedin_url = contact["linkedin"]
            if contact.get("github") and not self.github_url:
                self.github_url = contact["github"]

        # Categorías
        if cv_data.get("categorized"):
            cat = cv_data["categorized"]
            if cat.get("languages"):
                self.languages.extend(cat["languages"])
                self.languages = list(set(self.languages))
            if cat.get("frameworks_backend") or cat.get("frameworks_frontend"):
                frameworks = cat.get("frameworks_backend", []) + cat.get("frameworks_frontend", [])
                self.frameworks.extend(frameworks)
                self.frameworks = list(set(self.frameworks))
            if cat.get("tools"):
                self.tools.extend(cat["tools"])
                self.tools = list(set(self.tools))

        self.sources["cv"] = "loaded"

    def merge_from_linkedin(self, linkedin_data: Dict):
        """Integra datos extraídos de LinkedIn"""
        # Aquí agregarías lógica para extraer info de LinkedIn
        # Por ahora marcamos que se intentó
        self.sources["linkedin"] = "loaded"

    def merge_from_github(self, github_data: Dict):
        """Integra datos extraídos de GitHub"""
        if github_data.get("name") and not self.name:
            self.name = github_data["name"]

        if github_data.get("bio"):
            self.bio = github_data["bio"]

        if github_data.get("location"):
            self.location = github_data["location"]

        if github_data.get("company"):
            if github_data["company"] not in self.companies:
                self.companies.append(github_data["company"])

        # Tecnologías y lenguajes
        if github_data.get("technologies"):
            for tech in github_data["technologies"]:
                tech_str = tech if isinstance(tech, str) else tech.get("name", tech.get("technology", ""))
                if tech_str and tech_str not in self.technologies:
                    self.technologies.append(tech_str)

        if github_data.get("top_languages"):
            for lang in github_data["top_languages"]:
                lang_str = lang if isinstance(lang, str) else lang.get("language", lang.get("name", ""))
                if lang_str and lang_str not in self.languages:
                    self.languages.append(lang_str)

        # Lenguajes con porcentaje (nuevo formato browser)
        if github_data.get("languages") and isinstance(github_data["languages"], list):
            for lang_obj in github_data["languages"]:
                if isinstance(lang_obj, dict) and lang_obj.get("language"):
                    if lang_obj["language"] not in self.languages:
                        self.languages.append(lang_obj["language"])

        # Frameworks y herramientas extraídas por browser
        if github_data.get("frameworks"):
            for fw in github_data["frameworks"]:
                fw_str = fw if isinstance(fw, str) else fw.get("name", fw.get("framework", ""))
                if fw_str and fw_str not in self.frameworks:
                    self.frameworks.append(fw_str)

        if github_data.get("tools"):
            for tool in github_data["tools"]:
                tool_str = tool if isinstance(tool, str) else tool.get("name", tool.get("tool", ""))
                if tool_str and tool_str not in self.tools:
                    self.tools.append(tool_str)

        # Proyectos notables
        if github_data.get("notable_projects"):
            self.notable_projects.extend(github_data["notable_projects"])

        # Repositorios destacados (nuevo formato browser)
        if github_data.get("repositories"):
            for repo in github_data["repositories"]:
                project = {
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo.get("stars", 0),
                    "url": repo.get("url")
                }
                # Solo agregar si no existe
                if not any(p.get("name") == project["name"] for p in self.notable_projects):
                    self.notable_projects.append(project)

        self.github_url = github_data.get("profile_url") or github_data.get("url")

        # Guardar métricas adicionales en sources para referencia
        github_metrics = {
            "status": "loaded",
            "followers": github_data.get("followers"),
            "public_repos": github_data.get("public_repos"),
            "contributions_last_year": github_data.get("contributions_last_year"),
            "activity_level": github_data.get("activity_level"),
            "specializations": github_data.get("specializations", [])
        }
        self.sources["github"] = github_metrics


if __name__ == "__main__":
    # Test del perfil
    profile = UserProfile()
    profile.name = "Vicente Rivas"
    profile.current_role = "Full Stack Developer"
    profile.technologies = ["Python", "JavaScript", "React", "Docker"]
    profile.years_of_experience = 5

    print("=== Perfil de Usuario ===")
    print(profile.generate_search_context())

    # Test guardar/cargar
    profile.save("test_profile.json")
    loaded = UserProfile.load("test_profile.json")
    print("\n=== Perfil Cargado ===")
    print(loaded.generate_search_context())
