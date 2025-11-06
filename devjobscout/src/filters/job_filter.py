"""
Sistema de filtros inteligentes para ofertas de trabajo
"""
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class FilterResult(Enum):
    """Resultado del filtrado"""
    PASS = "pass"
    REJECT = "reject"


@dataclass
class FilterScore:
    """Score detallado del filtrado"""
    passed: bool
    score: float  # 0-100
    reasons: List[str]
    warnings: List[str]


class JobFilter:
    """Filtro inteligente de ofertas de trabajo"""

    def __init__(
        self,
        tech_stack: List[str],
        toxic_keywords: List[str],
        min_salary: Optional[int] = None,
        required_keywords: Optional[List[str]] = None,
        location_keywords: Optional[List[str]] = None
    ):
        """
        Inicializa el filtro

        Args:
            tech_stack: Stack tecnológico del usuario
            toxic_keywords: Palabras tóxicas a filtrar
            min_salary: Salario mínimo aceptable
            required_keywords: Keywords que DEBEN estar presentes
            location_keywords: Ubicaciones aceptables
        """
        self.tech_stack = [t.lower() for t in tech_stack]
        self.toxic_keywords = [k.lower() for k in toxic_keywords]
        self.min_salary = min_salary
        self.required_keywords = [k.lower() for k in (required_keywords or [])]
        self.location_keywords = [k.lower() for k in (location_keywords or [])]

    def filter_job(self, job: Dict[str, Any]) -> FilterScore:
        """
        Filtra una oferta de trabajo

        Args:
            job: Diccionario con datos de la oferta
                 Campos esperados: title, description, company, location,
                                  salary (opcional), url

        Returns:
            FilterScore con resultado del análisis
        """
        score = 100.0
        reasons = []
        warnings = []

        # Preparar texto combinado para análisis
        text_to_analyze = f"{job.get('title', '')} {job.get('description', '')}".lower()

        # 1. Verificar palabras tóxicas (RECHAZO AUTOMÁTICO)
        toxic_found = self._check_toxic_keywords(text_to_analyze)
        if toxic_found:
            return FilterScore(
                passed=False,
                score=0.0,
                reasons=[f"Contiene palabra tóxica: {', '.join(toxic_found)}"],
                warnings=[]
            )

        # 2. Verificar match con tech stack (0-40 puntos)
        stack_match, stack_details = self._check_tech_stack_match(text_to_analyze)
        score += stack_match
        if stack_details:
            reasons.append(f"Stack match: {stack_details}")
        else:
            warnings.append("No se encontró ninguna tecnología del stack")
            score -= 20

        # 3. Verificar keywords requeridas (0-20 puntos)
        if self.required_keywords:
            required_match = self._check_required_keywords(text_to_analyze)
            if not required_match:
                return FilterScore(
                    passed=False,
                    score=0.0,
                    reasons=["No contiene keywords requeridas"],
                    warnings=[]
                )
            score += 20
            reasons.append("Contiene keywords requeridas")

        # 4. Verificar ubicación (0-15 puntos)
        if self.location_keywords:
            location_match = self._check_location(job.get('location', '').lower())
            if location_match:
                score += 15
                reasons.append(f"Ubicación coincide: {location_match}")
            else:
                warnings.append("Ubicación no coincide con preferencias")
                score -= 10

        # 5. Verificar salario si está disponible (0-15 puntos)
        if self.min_salary and 'salary' in job:
            salary_check, salary_reason = self._check_salary(job.get('salary'))
            if salary_check:
                score += 15
                reasons.append(salary_reason)
            else:
                warnings.append(salary_reason)
                score -= 15

        # 6. Verificar señales positivas (0-10 puntos)
        positive_signals = self._check_positive_signals(text_to_analyze)
        if positive_signals:
            score += 10
            reasons.append(f"Señales positivas: {', '.join(positive_signals)}")

        # Normalizar score (0-100)
        score = max(0, min(100, score))

        # Decisión final: score >= 60 es PASS
        passed = score >= 60

        return FilterScore(
            passed=passed,
            score=score,
            reasons=reasons,
            warnings=warnings
        )

    def _check_toxic_keywords(self, text: str) -> List[str]:
        """Detecta palabras tóxicas en el texto"""
        found = []
        for keyword in self.toxic_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found.append(keyword)
        return found

    def _check_tech_stack_match(self, text: str) -> tuple[float, str]:
        """
        Verifica match con tech stack del usuario

        Returns:
            (score, descripción del match)
        """
        matches = []
        for tech in self.tech_stack:
            pattern = r'\b' + re.escape(tech) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(tech)

        if not matches:
            return 0.0, ""

        # Score basado en porcentaje de match
        match_ratio = len(matches) / len(self.tech_stack)
        score = min(40, match_ratio * 50)  # Max 40 puntos

        details = f"{len(matches)}/{len(self.tech_stack)} tecnologías ({', '.join(matches[:3])}...)"
        return score, details

    def _check_required_keywords(self, text: str) -> bool:
        """Verifica que todos los keywords requeridos estén presentes"""
        for keyword in self.required_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if not re.search(pattern, text, re.IGNORECASE):
                return False
        return True

    def _check_location(self, location: str) -> Optional[str]:
        """Verifica si la ubicación coincide"""
        for loc in self.location_keywords:
            if loc in location:
                return loc
        return None

    def _check_salary(self, salary: Any) -> tuple[bool, str]:
        """Verifica si el salario cumple requisitos"""
        if not salary:
            return False, "Salario no especificado"

        # Intentar extraer número de salario
        salary_str = str(salary)
        numbers = re.findall(r'\d+', salary_str.replace(',', '').replace('.', ''))

        if not numbers:
            return False, "No se pudo determinar el salario"

        # Tomar el número más grande encontrado
        max_salary = max(int(n) for n in numbers)

        if max_salary >= self.min_salary:
            return True, f"Salario cumple requisito: {max_salary}€"
        else:
            return False, f"Salario muy bajo: {max_salary}€"

    def _check_positive_signals(self, text: str) -> List[str]:
        """Detecta señales positivas en la oferta"""
        positive_keywords = {
            "remote": "trabajo remoto",
            "flexible": "horario flexible",
            "learning": "oportunidades de aprendizaje",
            "career growth": "desarrollo profesional",
            "mentorship": "mentoría",
            "benefits": "buenos beneficios",
            "equity": "equity/acciones",
            "vacation": "buenas vacaciones",
            "health insurance": "seguro médico",
            "work-life balance": "equilibrio vida-trabajo",
        }

        found = []
        for keyword, description in positive_keywords.items():
            if keyword in text:
                found.append(description)

        return found[:3]  # Max 3 señales

    @staticmethod
    def filter_jobs_batch(
        jobs: List[Dict[str, Any]],
        tech_stack: List[str],
        toxic_keywords: List[str],
        min_salary: Optional[int] = None,
        min_score: float = 60.0
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Filtra un lote de ofertas

        Args:
            jobs: Lista de ofertas
            tech_stack: Stack tecnológico
            toxic_keywords: Palabras tóxicas
            min_salary: Salario mínimo
            min_score: Score mínimo para aprobar

        Returns:
            Diccionario con 'passed' y 'rejected'
        """
        filter_instance = JobFilter(tech_stack, toxic_keywords, min_salary)

        passed = []
        rejected = []

        for job in jobs:
            result = filter_instance.filter_job(job)

            # Agregar score al job
            job_with_score = {**job, "filter_score": result.score}

            if result.passed and result.score >= min_score:
                job_with_score["filter_reasons"] = result.reasons
                passed.append(job_with_score)
            else:
                job_with_score["reject_reasons"] = result.reasons + result.warnings
                rejected.append(job_with_score)

        # Ordenar por score
        passed.sort(key=lambda x: x["filter_score"], reverse=True)
        rejected.sort(key=lambda x: x["filter_score"], reverse=True)

        return {
            "passed": passed,
            "rejected": rejected,
            "stats": {
                "total": len(jobs),
                "passed": len(passed),
                "rejected": len(rejected),
                "pass_rate": f"{len(passed)/len(jobs)*100:.1f}%" if jobs else "0%"
            }
        }


# Ejemplo de uso
if __name__ == "__main__":
    # Jobs de ejemplo
    sample_jobs = [
        {
            "title": "Senior Python Developer",
            "description": "Looking for a Python developer with Django and PostgreSQL experience. Remote work available.",
            "company": "Tech Company",
            "location": "Spain",
            "url": "https://example.com/job1"
        },
        {
            "title": "Rockstar Full Stack Developer",
            "description": "Fast-paced startup looking for a ninja developer who can wear many hats.",
            "company": "Toxic Startup",
            "location": "Madrid",
            "url": "https://example.com/job2"
        },
        {
            "title": "Node.js Backend Engineer",
            "description": "Work with Node.js, Express, MongoDB. Great work-life balance and mentorship.",
            "company": "Good Company",
            "location": "Remote - Spain",
            "url": "https://example.com/job3"
        }
    ]

    # Stack del usuario
    tech_stack = ["Python", "Django", "Node.js", "PostgreSQL", "MongoDB"]
    toxic_keywords = ["rockstar", "ninja", "fast-paced", "wear many hats"]

    # Filtrar
    results = JobFilter.filter_jobs_batch(sample_jobs, tech_stack, toxic_keywords)

    print("=== OFERTAS APROBADAS ===")
    for job in results["passed"]:
        print(f"\n{job['title']} - Score: {job['filter_score']:.1f}")
        print(f"Razones: {', '.join(job['filter_reasons'])}")

    print("\n\n=== OFERTAS RECHAZADAS ===")
    for job in results["rejected"]:
        print(f"\n{job['title']} - Score: {job['filter_score']:.1f}")
        print(f"Razones: {', '.join(job['reject_reasons'])}")

    print(f"\n\n=== ESTADÍSTICAS ===")
    print(f"Total: {results['stats']['total']}")
    print(f"Aprobadas: {results['stats']['passed']}")
    print(f"Rechazadas: {results['stats']['rejected']}")
    print(f"Tasa de aprobación: {results['stats']['pass_rate']}")
