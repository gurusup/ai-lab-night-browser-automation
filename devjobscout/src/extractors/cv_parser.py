"""
Parser de CV para extraer stack tecnológico desde archivos locales
"""
from typing import List, Dict, Optional
import re
from pathlib import Path


class CVParser:
    """Parser para extraer tecnologías de CVs/Portfolios locales"""

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

    def parse_from_text(self, text: str) -> List[str]:
        """
        Extrae tecnologías desde texto plano

        Args:
            text: Texto del CV/Portfolio

        Returns:
            Lista de tecnologías encontradas
        """
        found_tech = []
        text_lower = text.lower()

        for category, keywords in self.TECH_KEYWORDS.items():
            for keyword in keywords:
                # Búsqueda case-insensitive con word boundaries
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_tech.append(keyword)

        return list(set(found_tech))

    def extract_full_profile_from_text(self, text: str) -> Dict:
        """
        Extrae perfil completo del CV: experiencia, roles, empresas, etc.

        Args:
            text: Texto completo del CV

        Returns:
            Dict con toda la información extraída
        """
        # Extraer tecnologías
        technologies = self.parse_from_text(text)
        categorized = self.categorize_technologies(technologies)

        # Extraer años de experiencia
        years_exp = self._extract_years_experience(text)

        # Extraer roles/títulos
        roles = self._extract_roles(text)

        # Extraer empresas
        companies = self._extract_companies(text)

        # Extraer información de contacto
        contact = self._extract_contact_info(text)

        return {
            "all": sorted(technologies),
            "categorized": categorized,
            "count": len(technologies),
            "years_experience": years_exp,
            "roles": roles,
            "companies": companies,
            "contact": contact,
            "bio": self._extract_bio(text)
        }

    def _extract_years_experience(self, text: str) -> int:
        """Extrae años de experiencia del CV"""
        text_lower = text.lower()

        # Patrones comunes
        patterns = [
            r'(\d+)\+?\s*(?:años|years)?\s*(?:de)?\s*(?:experiencia|experience)',
            r'experience.*?(\d+)\+?\s*(?:años|years)',
            r'(\d+)\+?\s*(?:years|años)\s*of\s*experience'
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))

        # Si no encuentra, intentar calcular por fechas
        return self._estimate_years_from_dates(text)

    def _estimate_years_from_dates(self, text: str) -> int:
        """Estima años de experiencia por fechas encontradas"""
        # Buscar años (2018-2023, etc.)
        year_pattern = r'\b(20\d{2})\b'
        years = [int(y) for y in re.findall(year_pattern, text)]

        if len(years) >= 2:
            return max(years) - min(years)

        return 0

    def _extract_roles(self, text: str) -> List[str]:
        """Extrae roles/títulos del CV"""
        roles = []
        text_lower = text.lower()

        # Keywords de roles comunes
        role_keywords = [
            "developer", "engineer", "architect", "lead", "manager",
            "senior", "junior", "mid-level", "full stack", "backend",
            "frontend", "devops", "data", "ml", "qa", "analyst"
        ]

        # Buscar líneas que contengan roles
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            # Si la línea contiene un rol y no es muy larga
            if any(keyword in line_lower for keyword in role_keywords) and len(line) < 80:
                # Limpiar y agregar
                cleaned = line.strip()
                if cleaned and not cleaned.startswith(('•', '-', '*', '·')):
                    roles.append(cleaned)

        return list(set(roles))[:5]  # Top 5 roles únicos

    def _extract_companies(self, text: str) -> List[str]:
        """Extrae nombres de empresas del CV"""
        companies = []

        # Patrones comunes
        # Buscar después de keywords como "Company:", "Employer:", etc.
        patterns = [
            r'(?:company|employer|organization):\s*([A-Z][A-Za-z\s&,.]+?)(?:\n|,|\d{4})',
            r'(?:at|@)\s+([A-Z][A-Za-z\s&,.]{2,30}?)(?:\n|,|\(|\d{4})',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            companies.extend([m.strip() for m in matches])

        return list(set(companies))[:10]  # Top 10 empresas únicas

    def _extract_contact_info(self, text: str) -> Dict:
        """Extrae información de contacto"""
        contact = {}

        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group()

        # Teléfono
        phone_pattern = r'[\+\d][\d\s\-\(\)]{8,}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group().strip()

        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact['linkedin'] = f"https://{linkedin_match.group()}"

        # GitHub
        github_pattern = r'github\.com/[\w\-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact['github'] = f"https://{github_match.group()}"

        return contact

    def _extract_bio(self, text: str) -> str:
        """Extrae bio/resumen del CV"""
        text_lines = text.split('\n')

        # Buscar secciones de resumen
        summary_keywords = ['summary', 'resumen', 'about', 'profile', 'objective', 'perfil']

        for i, line in enumerate(text_lines):
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in summary_keywords):
                # Tomar las siguientes 3-5 líneas como bio
                bio_lines = []
                for j in range(i+1, min(i+6, len(text_lines))):
                    if text_lines[j].strip() and not text_lines[j].isupper():
                        bio_lines.append(text_lines[j].strip())
                    elif len(bio_lines) > 0:
                        break

                if bio_lines:
                    return ' '.join(bio_lines)

        # Si no encuentra sección explícita, tomar primeras líneas significativas
        meaningful_lines = [l.strip() for l in text_lines if len(l.strip()) > 50]
        if meaningful_lines:
            return meaningful_lines[0]

        return ""

    def parse_from_file(self, file_content: bytes, file_type: str) -> List[str]:
        """
        Extrae tecnologías desde un archivo

        Args:
            file_content: Contenido del archivo en bytes
            file_type: Tipo de archivo ('pdf', 'txt', 'docx')

        Returns:
            Lista de tecnologías encontradas
        """
        if file_type == 'txt':
            text = file_content.decode('utf-8', errors='ignore')
        elif file_type == 'pdf':
            text = self._extract_text_from_pdf(file_content)
        elif file_type == 'docx':
            text = self._extract_text_from_docx(file_content)
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file_type}")

        return self.parse_from_text(text)

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extrae texto de un PDF"""
        try:
            import io
            from pypdf import PdfReader

            pdf_file = io.BytesIO(pdf_content)
            reader = PdfReader(pdf_file)

            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            return text
        except ImportError:
            print("⚠️  pypdf no está instalado. Instalando...")
            import subprocess
            subprocess.run(["pip", "install", "pypdf"], check=True)
            return self._extract_text_from_pdf(pdf_content)
        except Exception as e:
            print(f"❌ Error leyendo PDF: {e}")
            return ""

    def _extract_text_from_docx(self, docx_content: bytes) -> str:
        """Extrae texto de un DOCX"""
        try:
            import io
            from docx import Document

            docx_file = io.BytesIO(docx_content)
            doc = Document(docx_file)

            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text
        except ImportError:
            print("⚠️  python-docx no está instalado. Instalando...")
            import subprocess
            subprocess.run(["pip", "install", "python-docx"], check=True)
            return self._extract_text_from_docx(docx_content)
        except Exception as e:
            print(f"❌ Error leyendo DOCX: {e}")
            return ""

    def categorize_technologies(self, technologies: List[str]) -> Dict[str, List[str]]:
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


# Función helper para uso rápido
def extract_stack_from_cv(file_content: bytes, file_type: str) -> Dict[str, any]:
    """
    Extrae perfil completo desde un CV

    Args:
        file_content: Contenido del archivo
        file_type: Tipo ('pdf', 'txt', 'docx')

    Returns:
        Diccionario con toda la información extraída
    """
    parser = CVParser()

    # Extraer texto del archivo
    if file_type == 'txt':
        text = file_content.decode('utf-8', errors='ignore')
    elif file_type == 'pdf':
        text = parser._extract_text_from_pdf(file_content)
    elif file_type == 'docx':
        text = parser._extract_text_from_docx(file_content)
    else:
        raise ValueError(f"Tipo de archivo no soportado: {file_type}")

    # Extraer perfil completo
    return parser.extract_full_profile_from_text(text)


if __name__ == "__main__":
    # Test con texto de ejemplo
    sample_cv = """
    CURRICULUM VITAE
    Vicente Rivas Monferrer

    EXPERIENCIA:
    Senior Full Stack Developer - Tech Company (2020-2024)
    - Desarrollo de aplicaciones web con React, Node.js y PostgreSQL
    - Implementación de pipelines CI/CD con Docker y Kubernetes
    - Integración con AWS (EC2, S3, Lambda)

    Backend Developer - Startup (2018-2020)
    - APIs RESTful con Python Django y Flask
    - Base de datos MongoDB y Redis
    - Despliegue en Azure

    HABILIDADES TÉCNICAS:
    - Lenguajes: Python, JavaScript, TypeScript, SQL
    - Frontend: React, Vue.js, Next.js
    - Backend: Django, Flask, FastAPI, Express
    - DevOps: Docker, Kubernetes, Terraform, GitHub Actions
    - Bases de datos: PostgreSQL, MongoDB, Redis
    - Cloud: AWS, Azure, GCP
    - IA/ML: TensorFlow, PyTorch, LangChain
    """

    parser = CVParser()
    technologies = parser.parse_from_text(sample_cv)
    categorized = parser.categorize_technologies(technologies)

    print("=== Tecnologías extraídas ===")
    print(f"Total: {len(technologies)}")
    print(f"Tecnologías: {', '.join(technologies)}")
    print("\n=== Categorizadas ===")
    for category, techs in categorized.items():
        if techs:
            print(f"{category}: {', '.join(techs)}")
