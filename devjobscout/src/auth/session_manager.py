"""
Gestor de sesiones y cookies para autenticación persistente
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import pickle


class SessionManager:
    """Gestiona sesiones de navegador y cookies para autenticación persistente"""

    def __init__(self, sessions_dir: str = "sessions"):
        """
        Inicializa el gestor de sesiones

        Args:
            sessions_dir: Directorio donde guardar las sesiones
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)

    def save_session(self, platform: str, cookies: List[Dict], metadata: Optional[Dict] = None):
        """
        Guarda cookies de una sesión autenticada

        Args:
            platform: Nombre de la plataforma (linkedin, google, etc.)
            cookies: Lista de cookies del navegador
            metadata: Información adicional (email, fecha, etc.)
        """
        session_file = self.sessions_dir / f"{platform}_session.json"

        session_data = {
            "platform": platform,
            "cookies": cookies,
            "saved_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        print(f"✅ Sesión guardada para {platform}")

    def load_session(self, platform: str) -> Optional[Dict]:
        """
        Carga cookies de una sesión guardada

        Args:
            platform: Nombre de la plataforma

        Returns:
            Datos de la sesión o None si no existe
        """
        session_file = self.sessions_dir / f"{platform}_session.json"

        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            print(f"✅ Sesión cargada para {platform}")
            return session_data
        except Exception as e:
            print(f"❌ Error cargando sesión de {platform}: {e}")
            return None

    def delete_session(self, platform: str):
        """
        Elimina una sesión guardada

        Args:
            platform: Nombre de la plataforma
        """
        session_file = self.sessions_dir / f"{platform}_session.json"

        if session_file.exists():
            session_file.unlink()
            print(f"✅ Sesión eliminada para {platform}")
        else:
            print(f"⚠️  No existe sesión para {platform}")

    def list_sessions(self) -> List[Dict]:
        """
        Lista todas las sesiones guardadas

        Returns:
            Lista de información de sesiones
        """
        sessions = []

        for session_file in self.sessions_dir.glob("*_session.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    sessions.append({
                        "platform": data["platform"],
                        "saved_at": data["saved_at"],
                        "has_cookies": len(data.get("cookies", [])) > 0,
                        "metadata": data.get("metadata", {})
                    })
            except Exception:
                continue

        return sessions

    def is_session_valid(self, platform: str) -> bool:
        """
        Verifica si existe una sesión válida para una plataforma

        Args:
            platform: Nombre de la plataforma

        Returns:
            True si existe y es válida
        """
        session_data = self.load_session(platform)

        if not session_data:
            return False

        # Verificar que tenga cookies
        cookies = session_data.get("cookies", [])
        return len(cookies) > 0

    def save_browser_state(self, platform: str, state_data: bytes):
        """
        Guarda el estado completo del navegador (para playwright/selenium)

        Args:
            platform: Nombre de la plataforma
            state_data: Estado serializado del navegador
        """
        state_file = self.sessions_dir / f"{platform}_browser_state.pkl"

        with open(state_file, 'wb') as f:
            pickle.dump(state_data, f)

        print(f"✅ Estado del navegador guardado para {platform}")

    def load_browser_state(self, platform: str) -> Optional[bytes]:
        """
        Carga el estado completo del navegador

        Args:
            platform: Nombre de la plataforma

        Returns:
            Estado del navegador o None
        """
        state_file = self.sessions_dir / f"{platform}_browser_state.pkl"

        if not state_file.exists():
            return None

        try:
            with open(state_file, 'rb') as f:
                state_data = pickle.load(f)
            return state_data
        except Exception as e:
            print(f"❌ Error cargando estado del navegador: {e}")
            return None


# Instancia global
session_manager = SessionManager()


# Funciones helper
def save_linkedin_session(cookies: List[Dict], email: Optional[str] = None):
    """Guarda sesión de LinkedIn"""
    session_manager.save_session(
        platform="linkedin",
        cookies=cookies,
        metadata={"email": email} if email else {}
    )


def load_linkedin_session() -> Optional[List[Dict]]:
    """Carga sesión de LinkedIn"""
    session = session_manager.load_session("linkedin")
    return session.get("cookies") if session else None


def save_google_session(cookies: List[Dict], email: Optional[str] = None):
    """Guarda sesión de Google"""
    session_manager.save_session(
        platform="google",
        cookies=cookies,
        metadata={"email": email} if email else {}
    )


def load_google_session() -> Optional[List[Dict]]:
    """Carga sesión de Google"""
    session = session_manager.load_session("google")
    return session.get("cookies") if session else None


if __name__ == "__main__":
    # Test del gestor de sesiones
    manager = SessionManager()

    # Simular guardado de sesión
    test_cookies = [
        {"name": "session_id", "value": "test123", "domain": ".linkedin.com"},
        {"name": "csrf_token", "value": "abc456", "domain": ".linkedin.com"}
    ]

    manager.save_session("linkedin", test_cookies, {"email": "test@example.com"})

    # Verificar carga
    loaded = manager.load_session("linkedin")
    print(f"Sesión cargada: {loaded}")

    # Listar sesiones
    sessions = manager.list_sessions()
    print(f"Sesiones disponibles: {sessions}")

    # Limpiar test
    manager.delete_session("linkedin")
