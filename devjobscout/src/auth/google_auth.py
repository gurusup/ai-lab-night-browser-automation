"""
Autenticación para Google (Drive, Docs, etc.)
"""
from playwright.async_api import async_playwright
import asyncio
from typing import Optional, List, Dict
from .session_manager import session_manager


class GoogleAuth:
    """Maneja autenticación de Google con Playwright"""

    def __init__(self):
        self.platform = "google"

    async def manual_login(self, headless: bool = False) -> bool:
        """
        Abre el navegador para que el usuario haga login manualmente en Google
        y guarda la sesión

        Args:
            headless: Si True, no muestra el navegador

        Returns:
            True si el login fue exitoso
        """
        print("🔐 Iniciando login manual de Google...")
        print("📝 Sigue estos pasos:")
        print("   1. Se abrirá un navegador")
        print("   2. Inicia sesión en Google")
        print("   3. Espera a ver tu cuenta (ej: Gmail, Drive)")
        print("   4. El navegador se cerrará y guardará la sesión")
        print("")

        # Usar Playwright directamente
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://accounts.google.com/")

            print("🌐 Navegador abierto en Google login")
            print("⏳ Esperando que hagas login... (tienes 5 minutos)")

            # Esperar hasta 5 minutos para que el usuario haga login
            try:
                await page.wait_for_url(
                    "**/myaccount.google.com/**",
                    timeout=300000  # 5 minutos
                )
                print("✅ Login detectado!")
            except Exception:
                print("⚠️  Timeout esperando login. Verificando...")

                # Verificar manualmente
                current_url = page.url
                if "myaccount.google.com" in current_url or "mail.google.com" in current_url:
                    print("✅ Login confirmado!")
                else:
                    print("❌ No se detectó login exitoso")
                    await browser.close()
                    return False

            # Guardar cookies
            cookies = await context.cookies()

            # Intentar obtener email
            email = None
            try:
                # Buscar el email en la página
                email_element = await page.query_selector('[data-email]')
                if email_element:
                    email = await email_element.get_attribute('data-email')
            except Exception:
                pass

            session_manager.save_session(
                platform=self.platform,
                cookies=cookies,
                metadata={"email": email, "login_type": "manual"}
            )

            print(f"✅ Sesión de Google guardada con {len(cookies)} cookies")
            await browser.close()
            return True

    def has_valid_session(self) -> bool:
        """Verifica si hay una sesión válida de Google"""
        return session_manager.is_session_valid(self.platform)

    def get_session_cookies(self) -> Optional[List[Dict]]:
        """Obtiene cookies de la sesión de Google"""
        session = session_manager.load_session(self.platform)
        return session.get("cookies") if session else None

    def delete_session(self):
        """Elimina la sesión de Google"""
        session_manager.delete_session(self.platform)
        print("✅ Sesión de Google eliminada")


async def setup_google_session() -> bool:
    """
    Helper para configurar sesión de Google

    Returns:
        True si fue exitoso
    """
    auth = GoogleAuth()
    return await auth.manual_login(headless=False)


if __name__ == "__main__":
    # Test de login manual de Google
    print("=== Test de Google Auth ===")
    print("1. Login manual")
    print("2. Verificar sesión existente")

    choice = input("Selecciona opción (1-2): ")

    if choice == "1":
        asyncio.run(setup_google_session())
    elif choice == "2":
        auth = GoogleAuth()
        if auth.has_valid_session():
            print("✅ Existe sesión válida de Google")
            cookies = auth.get_session_cookies()
            print(f"   Cookies guardadas: {len(cookies)}")
        else:
            print("❌ No hay sesión válida. Ejecuta login manual primero.")
