"""
Configuración centralizada de DevJobScout
"""
import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class JobSearchConfig:
    """Configuración de búsqueda de empleos"""

    # Stack tecnológico del usuario
    tech_stack: List[str] = field(default_factory=list)

    # URLs de perfil
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # Filtros de búsqueda
    location: str = "Spain"
    remote_only: bool = True
    published_within_days: int = 7
    min_salary: Optional[int] = None

    # Palabras tóxicas a filtrar
    toxic_keywords: List[str] = field(default_factory=lambda: [
        "rockstar",
        "ninja",
        "guru",
        "fast-paced",
        "wear many hats",
        "family",
        "hustle",
        "grind",
    ])

    # Plataformas habilitadas
    platforms: List[str] = field(default_factory=lambda: [
        "linkedin",
        "infojobs",
        "remoteok"
    ])

    # Límites de resultados
    max_results_per_platform: int = 10
    min_results_to_notify: int = 3

    # Notificaciones
    notify_telegram: bool = False
    notify_notion: bool = False


@dataclass
class BrowserConfig:
    """Configuración del navegador"""

    headless: bool = False
    use_vision: bool = True
    save_logs: bool = True
    log_path: str = "logs"


@dataclass
class NotificationConfig:
    """Configuración de notificaciones"""

    # Telegram
    telegram_bot_token: Optional[str] = field(
        default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN")
    )
    telegram_chat_id: Optional[str] = field(
        default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID")
    )

    # Notion
    notion_token: Optional[str] = field(
        default_factory=lambda: os.getenv("NOTION_TOKEN")
    )
    notion_database_id: Optional[str] = field(
        default_factory=lambda: os.getenv("NOTION_DATABASE_ID")
    )


@dataclass
class AppConfig:
    """Configuración principal de la aplicación"""

    browser_use_api_key: str = field(
        default_factory=lambda: os.getenv("BROWSER_USE_API_KEY", "")
    )

    job_search: JobSearchConfig = field(default_factory=JobSearchConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)

    # Rutas
    data_dir: str = "src/data"
    output_file: str = "src/data/all_jobs.json"


# Instancia global
config = AppConfig()
