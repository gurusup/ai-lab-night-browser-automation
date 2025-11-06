"""
Analizador de perfil para sugerencias automáticas de roles
"""
from typing import Dict, List, Tuple
import re
from collections import Counter


class ProfileAnalyzer:
    """Analiza el perfil completo y sugiere roles ideales"""

    # Mapeo de tecnologías a roles
    ROLE_PATTERNS = {
        "Full Stack Developer": {
            "required": ["frontend", "backend"],
            "technologies": ["React", "Vue.js", "Angular", "Node.js", "Django", "Flask", "Express", "Next.js"],
            "min_tech_count": 4,
            "keywords": ["full stack", "fullstack"]
        },
        "Backend Developer": {
            "required": ["backend"],
            "technologies": ["Python", "Django", "Flask", "FastAPI", "Node.js", "Express", "Java", "Spring", ".NET", "Go", "Ruby"],
            "databases": ["PostgreSQL", "MongoDB", "MySQL", "Redis"],
            "min_tech_count": 3,
            "keywords": ["backend", "api", "microservices"]
        },
        "Frontend Developer": {
            "required": ["frontend"],
            "technologies": ["React", "Vue.js", "Angular", "Svelte", "Next.js", "TypeScript", "JavaScript"],
            "min_tech_count": 2,
            "keywords": ["frontend", "ui", "ux"]
        },
        "DevOps Engineer": {
            "required": ["devops"],
            "technologies": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Ansible", "Jenkins", "GitLab CI", "GitHub Actions"],
            "min_tech_count": 3,
            "keywords": ["devops", "infrastructure", "ci/cd", "cloud"]
        },
        "Data Engineer": {
            "required": ["data"],
            "technologies": ["Python", "Spark", "Airflow", "Kafka", "SQL", "BigQuery", "Redshift", "Snowflake"],
            "databases": ["PostgreSQL", "MongoDB", "Cassandra", "Elasticsearch"],
            "min_tech_count": 3,
            "keywords": ["data engineer", "data pipeline", "etl"]
        },
        "Machine Learning Engineer": {
            "required": ["ml"],
            "technologies": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "Pandas", "NumPy"],
            "min_tech_count": 3,
            "keywords": ["machine learning", "ml", "ai", "deep learning"]
        },
        "Cloud Architect": {
            "required": ["cloud"],
            "technologies": ["AWS", "Azure", "GCP", "Terraform", "Docker", "Kubernetes"],
            "min_tech_count": 3,
            "keywords": ["cloud", "architecture", "infrastructure"]
        },
        "Mobile Developer": {
            "required": ["mobile"],
            "technologies": ["React Native", "Flutter", "Swift", "Kotlin", "Android", "iOS"],
            "min_tech_count": 1,
            "keywords": ["mobile", "app", "ios", "android"]
        }
    }

    def __init__(self):
        pass

    def analyze_profile(self, profile: 'UserProfile') -> Dict:
        """
        Analiza el perfil completo y genera recomendaciones

        Args:
            profile: UserProfile object

        Returns:
            Dict con análisis y recomendaciones
        """
        # Extraer información
        all_tech = profile.technologies + profile.languages + profile.frameworks + profile.tools

        # Normalizar: convertir dicts a strings (GitHub browser extraction devuelve dicts)
        normalized_tech = []
        for t in all_tech:
            if isinstance(t, dict):
                # Extraer nombre del lenguaje/tech del formato dict
                if 'language' in t:
                    normalized_tech.append(t['language'])
                elif 'name' in t:
                    normalized_tech.append(t['name'])
            elif isinstance(t, str):
                normalized_tech.append(t)

        all_tech_lower = [t.lower() for t in normalized_tech]

        # Detectar categorías principales
        categories = self._detect_categories(all_tech_lower, profile.bio or "")

        # Calcular años de experiencia
        years_exp = profile.years_of_experience or self._estimate_experience(profile)

        # Detectar nivel (Junior/Mid/Senior)
        level = self._detect_level(years_exp, len(normalized_tech), profile)

        # Sugerir roles
        suggested_roles = self._suggest_roles(normalized_tech, categories, profile.bio or "")

        # Extraer soft skills del bio y proyectos
        soft_skills = self._extract_soft_skills(profile)

        # Generar query de búsqueda optimizada
        search_queries = self._generate_search_queries(suggested_roles, normalized_tech[:10], level)

        return {
            "suggested_roles": suggested_roles,
            "level": level,
            "years_experience": years_exp,
            "categories": categories,
            "hard_skills": {
                "technologies": profile.technologies[:15],
                "languages": profile.languages[:8],
                "frameworks": profile.frameworks[:8],
                "tools": profile.tools[:8]
            },
            "soft_skills": soft_skills,
            "search_queries": search_queries,
            "profile_strength": self._calculate_profile_strength(profile)
        }

    def _detect_categories(self, tech_lower: List[str], bio: str) -> List[str]:
        """Detecta categorías principales del perfil"""
        categories = []
        bio_lower = bio.lower()

        # Frontend
        frontend_tech = ["react", "vue", "angular", "svelte", "nextjs", "javascript", "typescript", "html", "css"]
        if any(t in tech_lower for t in frontend_tech) or "frontend" in bio_lower:
            categories.append("frontend")

        # Backend
        backend_tech = ["django", "flask", "fastapi", "nodejs", "express", "spring", "rails", "laravel"]
        if any(t in tech_lower for t in backend_tech) or "backend" in bio_lower:
            categories.append("backend")

        # DevOps
        devops_tech = ["docker", "kubernetes", "aws", "azure", "terraform", "jenkins", "ci/cd"]
        if any(t in tech_lower for t in devops_tech) or any(word in bio_lower for word in ["devops", "infrastructure", "cloud"]):
            categories.append("devops")

        # Data
        data_tech = ["spark", "airflow", "kafka", "pandas", "numpy", "bigquery"]
        if any(t in tech_lower for t in data_tech) or any(word in bio_lower for word in ["data engineer", "data pipeline"]):
            categories.append("data")

        # ML/AI
        ml_tech = ["tensorflow", "pytorch", "keras", "scikit-learn"]
        if any(t in tech_lower for t in ml_tech) or any(word in bio_lower for word in ["machine learning", "deep learning", "ai"]):
            categories.append("ml")

        # Mobile
        mobile_tech = ["react native", "flutter", "swift", "kotlin", "android", "ios"]
        if any(t in tech_lower for t in mobile_tech) or "mobile" in bio_lower:
            categories.append("mobile")

        # Cloud
        cloud_tech = ["aws", "azure", "gcp", "google cloud"]
        if any(t in tech_lower for t in cloud_tech):
            categories.append("cloud")

        return categories

    def _detect_level(self, years_exp: int, tech_count: int, profile: 'UserProfile') -> str:
        """Detecta el nivel del candidato"""
        # Factores para determinar nivel
        has_leadership = any(keyword in (profile.bio or "").lower()
                           for keyword in ["lead", "senior", "architect", "manager", "team lead"])

        project_count = len(profile.notable_projects)

        # Lógica de nivel
        if years_exp >= 7 or has_leadership:
            return "Senior"
        elif years_exp >= 3 or (tech_count >= 15 and project_count >= 3):
            return "Mid-Level"
        else:
            return "Junior"

    def _estimate_experience(self, profile: 'UserProfile') -> int:
        """Estima años de experiencia si no está especificado"""
        # Basado en número de empresas y proyectos
        company_count = len(profile.companies)
        project_count = len(profile.notable_projects)
        tech_count = len(profile.technologies)

        # Estimación conservadora
        estimated = 0
        if company_count >= 3:
            estimated = 4
        elif company_count == 2:
            estimated = 2
        elif company_count == 1:
            estimated = 1

        # Ajustar por proyectos y tecnologías
        if project_count >= 5 and tech_count >= 20:
            estimated = max(estimated, 3)

        return estimated

    def _suggest_roles(self, all_tech: List[str], categories: List[str], bio: str) -> List[Tuple[str, int]]:
        """
        Sugiere roles basándose en tecnologías y categorías

        Returns:
            Lista de tuplas (rol, score) ordenadas por score
        """
        tech_lower = [t.lower() for t in all_tech]
        bio_lower = bio.lower()
        role_scores = {}

        for role_name, pattern in self.ROLE_PATTERNS.items():
            score = 0

            # Check required categories
            if "required" in pattern:
                required_match = any(req in categories for req in pattern["required"])
                if not required_match:
                    continue

            # Score por tecnologías
            if "technologies" in pattern:
                tech_matches = sum(1 for t in pattern["technologies"] if t.lower() in tech_lower)
                if tech_matches >= pattern.get("min_tech_count", 2):
                    score += tech_matches * 10

            # Score por bases de datos (para roles backend/data)
            if "databases" in pattern:
                db_matches = sum(1 for db in pattern["databases"] if db.lower() in tech_lower)
                score += db_matches * 5

            # Score por keywords en bio
            if "keywords" in pattern:
                keyword_matches = sum(1 for kw in pattern["keywords"] if kw in bio_lower)
                score += keyword_matches * 15

            # Solo agregar si tiene score > 0
            if score > 0:
                role_scores[role_name] = score

        # Ordenar por score y retornar top 5
        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_roles[:5]

    def _extract_soft_skills(self, profile: 'UserProfile') -> List[str]:
        """Extrae soft skills del bio y contexto"""
        soft_skills = []
        bio_text = (profile.bio or "").lower()

        skill_keywords = {
            "Team Leadership": ["lead", "team", "manage", "mentor"],
            "Communication": ["present", "documentation", "collaborate", "communication"],
            "Problem Solving": ["problem solving", "analytical", "troubleshoot"],
            "Agile": ["agile", "scrum", "kanban"],
            "Project Management": ["project", "planning", "coordination"],
            "Self-motivated": ["self-motivated", "independent", "autonomous"]
        }

        for skill, keywords in skill_keywords.items():
            if any(kw in bio_text for kw in keywords):
                soft_skills.append(skill)

        # Si no hay soft skills del bio, agregar genéricas
        if not soft_skills:
            soft_skills = ["Team Collaboration", "Problem Solving", "Continuous Learning"]

        return soft_skills

    def _generate_search_queries(self, suggested_roles: List[Tuple[str, int]], top_tech: List[str], level: str) -> List[str]:
        """
        Genera queries de búsqueda optimizadas

        Args:
            suggested_roles: Lista de (role, score)
            top_tech: Top tecnologías
            level: Junior/Mid-Level/Senior

        Returns:
            Lista de queries optimizadas
        """
        queries = []

        # Top 3 roles con nivel
        for role, score in suggested_roles[:3]:
            if level == "Senior":
                queries.append(f"Senior {role}")
            elif level == "Mid-Level":
                queries.append(f"{role}")
            else:
                queries.append(f"Junior {role}")

        # Query con top tecnologías
        if top_tech:
            tech_str = " ".join(top_tech[:3])
            queries.append(f"{tech_str} Developer")

        return queries

    def _calculate_profile_strength(self, profile: 'UserProfile') -> int:
        """
        Calcula la fortaleza del perfil (0-100)

        Factores:
        - Cantidad de tecnologías
        - Proyectos notables
        - Experiencia
        - Bio completado
        - Enlaces (LinkedIn, GitHub)
        """
        score = 0

        # Tecnologías (max 30 puntos)
        tech_count = len(profile.technologies) + len(profile.languages) + len(profile.frameworks)
        score += min(tech_count * 2, 30)

        # Proyectos (max 20 puntos)
        project_count = len(profile.notable_projects)
        score += min(project_count * 4, 20)

        # Experiencia (max 20 puntos)
        if profile.years_of_experience:
            score += min(profile.years_of_experience * 3, 20)
        elif len(profile.companies) > 0:
            score += len(profile.companies) * 5

        # Bio completo (10 puntos)
        if profile.bio and len(profile.bio) > 50:
            score += 10

        # Enlaces (max 20 puntos)
        if profile.linkedin_url:
            score += 7
        if profile.github_url:
            score += 7
        if profile.portfolio_url:
            score += 6

        return min(score, 100)


def analyze_profile_and_suggest(profile: 'UserProfile') -> Dict:
    """
    Helper function para analizar perfil y obtener sugerencias

    Args:
        profile: UserProfile object

    Returns:
        Dict con análisis completo
    """
    analyzer = ProfileAnalyzer()
    return analyzer.analyze_profile(profile)
