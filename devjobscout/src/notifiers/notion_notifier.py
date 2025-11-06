"""
Notificador de Notion para DevJobScout
"""
from typing import List, Dict, Optional
from notion_client import Client
from notion_client.errors import APIResponseError


class NotionNotifier:
    """Agrega ofertas de trabajo a una base de datos de Notion"""

    def __init__(self, notion_token: str, database_id: str):
        """
        Inicializa el notificador de Notion

        Args:
            notion_token: Token de integración de Notion
            database_id: ID de la base de datos donde agregar ofertas
        """
        self.client = Client(auth=notion_token)
        self.database_id = database_id

    def add_job(self, job: Dict) -> bool:
        """
        Agrega una oferta individual a Notion

        Args:
            job: Diccionario con datos de la oferta

        Returns:
            True si se agregó correctamente
        """
        try:
            properties = self._build_job_properties(job)
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            return True
        except APIResponseError as e:
            print(f"❌ Error agregando oferta a Notion: {e}")
            return False

    def add_jobs_batch(self, jobs: List[Dict]) -> int:
        """
        Agrega múltiples ofertas a Notion

        Args:
            jobs: Lista de ofertas

        Returns:
            Número de ofertas agregadas exitosamente
        """
        added_count = 0

        for job in jobs:
            if self.add_job(job):
                added_count += 1

        return added_count

    def _build_job_properties(self, job: Dict) -> Dict:
        """
        Construye el objeto de properties para Notion

        Args:
            job: Datos de la oferta

        Returns:
            Diccionario de properties compatible con Notion API
        """
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": job.get('title', 'Sin título')
                        }
                    }
                ]
            },
            "Company": {
                "rich_text": [
                    {
                        "text": {
                            "content": job.get('company', 'Sin empresa')
                        }
                    }
                ]
            },
            "Location": {
                "rich_text": [
                    {
                        "text": {
                            "content": job.get('location', 'Sin ubicación')
                        }
                    }
                ]
            },
            "URL": {
                "url": job.get('url')
            },
            "Status": {
                "select": {
                    "name": "Nueva"
                }
            }
        }

        # Agregar campos opcionales si existen
        if 'salary' in job and job['salary']:
            properties["Salary"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": str(job['salary'])
                        }
                    }
                ]
            }

        if 'filter_score' in job:
            properties["Score"] = {
                "number": round(job['filter_score'], 1)
            }

        if 'description' in job and job['description']:
            properties["Description"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": job['description'][:2000]  # Notion limit
                        }
                    }
                ]
            }

        if 'platform' in job:
            properties["Platform"] = {
                "select": {
                    "name": job['platform'].capitalize()
                }
            }

        if 'tags' in job and job['tags']:
            # Convertir lista de tags a multi-select
            properties["Tags"] = {
                "multi_select": [
                    {"name": tag} for tag in job['tags'][:10]  # Max 10 tags
                ]
            }

        return properties

    def check_database_exists(self) -> bool:
        """
        Verifica que la base de datos existe y es accesible

        Returns:
            True si la base de datos es accesible
        """
        try:
            self.client.databases.retrieve(database_id=self.database_id)
            return True
        except APIResponseError as e:
            print(f"❌ Error accediendo a la base de datos de Notion: {e}")
            return False

    def get_database_properties(self) -> Optional[Dict]:
        """
        Obtiene las propiedades de la base de datos

        Returns:
            Diccionario con las propiedades o None si hay error
        """
        try:
            db = self.client.databases.retrieve(database_id=self.database_id)
            return db.get('properties', {})
        except APIResponseError as e:
            print(f"❌ Error obteniendo propiedades: {e}")
            return None


# Función helper para uso rápido
def notify_jobs_notion(
    notion_token: str,
    database_id: str,
    jobs: List[Dict]
) -> int:
    """
    Notifica ofertas agregándolas a Notion

    Args:
        notion_token: Token de Notion
        database_id: ID de la base de datos
        jobs: Lista de ofertas

    Returns:
        Número de ofertas agregadas
    """
    notifier = NotionNotifier(notion_token, database_id)
    return notifier.add_jobs_batch(jobs)


# Función para crear base de datos de ejemplo
def create_jobs_database_template(notion_token: str, parent_page_id: str) -> Optional[str]:
    """
    Crea una base de datos de plantilla para DevJobScout

    Args:
        notion_token: Token de Notion
        parent_page_id: ID de la página padre donde crear la DB

    Returns:
        ID de la base de datos creada o None si hay error
    """
    client = Client(auth=notion_token)

    try:
        database = client.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[
                {
                    "type": "text",
                    "text": {"content": "DevJobScout - Ofertas de Trabajo"}
                }
            ],
            properties={
                "Name": {"title": {}},
                "Company": {"rich_text": {}},
                "Location": {"rich_text": {}},
                "URL": {"url": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Nueva", "color": "blue"},
                            {"name": "Revisada", "color": "yellow"},
                            {"name": "Aplicada", "color": "green"},
                            {"name": "Descartada", "color": "red"}
                        ]
                    }
                },
                "Score": {"number": {"format": "number"}},
                "Salary": {"rich_text": {}},
                "Description": {"rich_text": {}},
                "Platform": {
                    "select": {
                        "options": [
                            {"name": "Linkedin", "color": "blue"},
                            {"name": "Infojobs", "color": "orange"},
                            {"name": "Remoteok", "color": "purple"}
                        ]
                    }
                },
                "Tags": {"multi_select": {}},
                "Date Added": {"date": {}}
            }
        )

        database_id = database['id']
        print(f"✅ Base de datos creada: {database_id}")
        return database_id

    except APIResponseError as e:
        print(f"❌ Error creando base de datos: {e}")
        return None


if __name__ == "__main__":
    # Test básico (necesitas configurar NOTION_TOKEN y NOTION_DATABASE_ID)
    import os
    from dotenv import load_dotenv

    load_dotenv()

    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")

    if token and db_id:
        notifier = NotionNotifier(token, db_id)

        # Verificar acceso
        if notifier.check_database_exists():
            print("✅ Conexión a Notion exitosa")

            # Test con oferta de ejemplo
            sample_job = {
                "title": "Senior Python Developer",
                "company": "Tech Company",
                "location": "Remote - Spain",
                "url": "https://example.com/job1",
                "filter_score": 85.5,
                "description": "Great opportunity for Python developers...",
                "platform": "linkedin"
            }

            if notifier.add_job(sample_job):
                print("✅ Oferta agregada a Notion")
        else:
            print("❌ No se pudo acceder a la base de datos")
    else:
        print("⚠️  Configura NOTION_TOKEN y NOTION_DATABASE_ID en .env para probar")
        print("   Puedes crear una integración en: https://www.notion.so/my-integrations")
