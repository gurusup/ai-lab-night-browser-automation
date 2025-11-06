"""
Autenticación para LinkedIn
"""
from playwright.async_api import async_playwright
import asyncio
from typing import Optional, Dict, List
from .session_manager import session_manager


class LinkedInAuth:
    """Maneja autenticación de LinkedIn con browser-use"""

    def __init__(self):
        self.platform = "linkedin"

    async def manual_login(self, headless: bool = False) -> bool:
        """
        Abre el navegador para que el usuario haga login manualmente
        y guarda la sesión

        Args:
            headless: Si True, no muestra el navegador (no recomendado para login manual)

        Returns:
            True si el login fue exitoso
        """
        print("🔐 Iniciando login manual de LinkedIn...")
        print("📝 Sigue estos pasos:")
        print("   1. Se abrirá un navegador")
        print("   2. Inicia sesión en LinkedIn")
        print("   3. Espera a que cargue tu feed/página principal")
        print("   4. El navegador se cerrará automáticamente y guardará la sesión")
        print("")

        # Usar Playwright directamente (más confiable para login manual)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://www.linkedin.com/login")

            print("🌐 Navegador abierto en LinkedIn login")
            print("⏳ Esperando que hagas login... (tienes 5 minutos)")

            # Esperar hasta 5 minutos para que el usuario haga login
            # Detectamos el login cuando la URL cambia al feed
            try:
                await page.wait_for_url(
                    "**/feed/**",
                    timeout=300000  # 5 minutos
                )
                print("✅ Login detectado!")
            except Exception:
                print("⚠️  Timeout esperando login. Verificando si estás logueado...")

                # Verificar si el login fue exitoso de otra forma
                current_url = page.url
                if "feed" in current_url or "mynetwork" in current_url:
                    print("✅ Login confirmado!")
                else:
                    print("❌ No se detectó login exitoso")
                    await browser.close()
                    return False

            # Guardar cookies
            cookies = await context.cookies()

            # Intentar obtener el email del usuario
            email = None
            try:
                # Navegar al perfil para obtener info
                await page.goto("https://www.linkedin.com/in/me/")
                await page.wait_for_load_state("networkidle", timeout=10000)

                # Intentar extraer email de la página (puede no estar visible)
                # Por ahora solo guardamos que el login fue exitoso
            except Exception:
                pass

            session_manager.save_session(
                platform=self.platform,
                cookies=cookies,
                metadata={"email": email, "login_type": "manual"}
            )

            print(f"✅ Sesión guardada con {len(cookies)} cookies")
            await browser.close()
            return True

    def has_valid_session(self) -> bool:
        """
        Verifica si hay una sesión válida guardada

        Returns:
            True si existe sesión válida
        """
        return session_manager.is_session_valid(self.platform)

    def get_session_cookies(self) -> Optional[List[Dict]]:
        """
        Obtiene las cookies de la sesión guardada

        Returns:
            Lista de cookies o None
        """
        session = session_manager.load_session(self.platform)
        return session.get("cookies") if session else None

    def delete_session(self):
        """Elimina la sesión guardada"""
        session_manager.delete_session(self.platform)
        print("✅ Sesión de LinkedIn eliminada")


async def setup_linkedin_session(method: str = "manual") -> bool:
    """
    Helper para configurar sesión de LinkedIn

    Args:
        method: "manual"

    Returns:
        True si fue exitoso
    """
    auth = LinkedInAuth()

    if method == "manual":
        return await auth.manual_login(headless=False)
    else:
        print("❌ Método no válido")
        return False


if __name__ == "__main__":
    # Test de login manual
    print("=== Test de LinkedIn Auth ===")
    print("1. Login manual")
    print("2. Verificar sesión existente")

    choice = input("Selecciona opción (1-2): ")

    if choice == "1":
        asyncio.run(setup_linkedin_session(method="manual"))
    elif choice == "2":
        auth = LinkedInAuth()
        if auth.has_valid_session():
            print("✅ Existe sesión válida de LinkedIn")
            cookies = auth.get_session_cookies()
            print(f"   Cookies guardadas: {len(cookies)}")
        else:
            print("❌ No hay sesión válida. Ejecuta login manual primero.")
