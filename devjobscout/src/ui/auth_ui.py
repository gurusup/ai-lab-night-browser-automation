"""
Interfaz de autenticación para Streamlit
"""
import streamlit as st
import asyncio
from typing import Optional
import sys
from pathlib import Path

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent))

from auth.linkedin_auth import LinkedInAuth, setup_linkedin_session
from auth.session_manager import session_manager


def render_auth_section():
    """Renderiza la sección de gestión de autenticación"""
    st.header("🔐 Autenticación de LinkedIn")

    st.markdown("""
    Para extraer información completa de LinkedIn, necesitas autenticarte.
    La sesión se guarda de forma segura y se reutiliza en futuras ejecuciones.
    """)

    # LinkedIn Auth
    st.subheader("🔵 LinkedIn")

    linkedin_auth = LinkedInAuth()
    has_linkedin = linkedin_auth.has_valid_session()

    if has_linkedin:
        st.success("✅ Sesión activa")
        session_info = session_manager.load_session("linkedin")
        if session_info:
            saved_at = session_info.get("saved_at", "Unknown")
            email = session_info.get("metadata", {}).get("email", "N/A")
            st.info(f"Guardada: {saved_at[:10]}")

        if st.button("🗑️ Eliminar sesión de LinkedIn", key="delete_linkedin"):
            linkedin_auth.delete_session()
            st.rerun()
    else:
        st.warning("⚠️ No hay sesión activa")

        st.markdown("**Opción 1: Login Manual** (Recomendado)")
        st.markdown("Se abrirá un navegador donde podrás hacer login normalmente")

        if st.button("🌐 Login Manual LinkedIn", key="login_manual_linkedin", type="primary"):
            with st.spinner("Abriendo navegador para login..."):
                try:
                    # Ejecutar login manual
                    success = asyncio.run(setup_linkedin_session(method="manual"))

                    if success:
                        st.success("✅ Login exitoso! Recarga la página")
                        st.balloons()
                    else:
                        st.error("❌ Login fallido. Inténtalo de nuevo")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        st.markdown("---")

        with st.expander("Opción 2: Login Automático (Puede fallar)"):
            st.warning("⚠️ LinkedIn puede bloquear logins automáticos. Usa login manual si falla.")

            email = st.text_input("Email de LinkedIn", key="linkedin_email")
            password = st.text_input("Contraseña", type="password", key="linkedin_password")

            if st.button("🔑 Login Automático", key="login_auto_linkedin"):
                if email and password:
                    with st.spinner("Intentando login automático..."):
                        try:
                            success = asyncio.run(setup_linkedin_session(
                                method="auto",
                                email=email,
                                password=password
                            ))

                            if success:
                                st.success("✅ Login exitoso!")
                                st.rerun()
                            else:
                                st.error("❌ Login fallido. Prueba login manual.")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                else:
                    st.error("Completa email y contraseña")

    st.markdown("---")

    # Información adicional
    with st.expander("ℹ️ Información sobre autenticación"):
        st.markdown("""
        ### ¿Por qué necesito autenticarme?

        - **LinkedIn**: Los perfiles tienen acceso limitado sin login. Con autenticación podrás extraer información más completa de tu perfil.

        ### ¿Es seguro?

        - Las sesiones se guardan **localmente** en tu máquina
        - Solo se guardan cookies, no contraseñas
        - Puedes eliminar las sesiones en cualquier momento

        ### ¿Cuánto duran las sesiones?

        - **LinkedIn**: ~1-2 semanas. Cuando expire, simplemente vuelve a hacer login.

        ### ¿Qué hacer si el login falla?

        1. **Login manual** siempre es más confiable
        2. Asegúrate de que tu cuenta no tenga 2FA activo (o complétalo durante el login)
        3. Si LinkedIn detecta actividad sospechosa, puede bloquear el acceso

        ### Ubicación de sesiones guardadas

        Las sesiones se guardan en: `devjobscout/sessions/`
        """)


def render_auth_status_indicator():
    """Renderiza indicadores de estado de autenticación en la barra lateral"""
    linkedin_auth = LinkedInAuth()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔐 Estado de Sesión")

    # LinkedIn
    if linkedin_auth.has_valid_session():
        st.sidebar.success("🔵 LinkedIn: Autenticado")
    else:
        st.sidebar.error("🔵 LinkedIn: Sin autenticar")


if __name__ == "__main__":
    st.set_page_config(page_title="Test Auth UI", layout="wide")
    render_auth_section()
