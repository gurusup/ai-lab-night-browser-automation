"""
DevJobScout - Interfaz principal con Streamlit
Tu reclutador personal silencioso 💼
"""
import streamlit as st
import asyncio
import json
from typing import List, Dict
import os

# Imports de módulos propios
from src.config.settings import AppConfig, JobSearchConfig
from src.extractors.stack_extractor import StackExtractor
from src.scrapers.linkedin_agent_v2 import LinkedInScraper
from src.scrapers.infojobs_agent import InfoJobsScraper
from src.scrapers.remoteok_agent import RemoteOKScraper
from src.filters.job_filter import JobFilter
from src.notifiers.telegram_notifier import TelegramNotifier
from src.notifiers.notion_notifier import NotionNotifier
from src.auth.linkedin_auth import LinkedInAuth, setup_linkedin_session
from src.auth.session_manager import session_manager
from src.ui.auth_ui import render_auth_section, render_auth_status_indicator
from src.extractors.cv_parser import CVParser, extract_stack_from_cv
from src.extractors.github_extractor import GitHubExtractor, extract_github_profile
from src.extractors.github_browser_extractor import GitHubBrowserExtractor, extract_github_profile_browser
from src.profile.user_profile import UserProfile
from src.profile.profile_analyzer import ProfileAnalyzer, analyze_profile_and_suggest


# Configuración de la página
st.set_page_config(
    page_title="DevJobScout",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Inicializa el estado de la sesión"""
    if 'config' not in st.session_state:
        st.session_state.config = AppConfig()
    if 'extracted_stack' not in st.session_state:
        st.session_state.extracted_stack = []
    if 'search_results' not in st.session_state:
        st.session_state.search_results = {}
    if 'filtered_jobs' not in st.session_state:
        st.session_state.filtered_jobs = []
    if 'user_profile' not in st.session_state:
        # Intentar cargar perfil guardado o crear uno nuevo
        st.session_state.user_profile = UserProfile.load()


def render_header():
    """Renderiza el header de la aplicación"""
    st.title("💼 DevJobScout")
    st.markdown("### Tu reclutador personal silencioso")
    st.markdown("---")


def render_sidebar():
    """Renderiza la barra lateral con configuración"""
    with st.sidebar:
        st.header("⚙️ Configuración")

        st.markdown("---")

        # Configuración de búsqueda
        st.subheader("🔎 Parámetros de Búsqueda")

        location = st.text_input(
            "Ubicación",
            value="Spain",
            help="Ubicación para la búsqueda de empleos"
        )

        remote_only = st.checkbox(
            "Solo trabajo remoto",
            value=True,
            help="Filtrar solo ofertas de trabajo remoto"
        )

        published_days = st.slider(
            "Publicado hace (días)",
            min_value=1,
            max_value=30,
            value=7,
            help="Ofertas publicadas en los últimos N días"
        )

        max_results = st.slider(
            "Resultados por plataforma",
            min_value=5,
            max_value=50,
            value=10,
            help="Número máximo de resultados por plataforma"
        )

        # Guardar en configuración
        st.session_state.config.job_search.location = location
        st.session_state.config.job_search.remote_only = remote_only
        st.session_state.config.job_search.published_within_days = published_days
        st.session_state.config.job_search.max_results_per_platform = max_results

        st.markdown("---")

        # Plataformas
        st.subheader("🌐 Plataformas")
        platforms = st.session_state.config.job_search.platforms

        use_linkedin = st.checkbox("LinkedIn", value="linkedin" in platforms)
        use_infojobs = st.checkbox("InfoJobs", value="infojobs" in platforms)
        use_remoteok = st.checkbox("RemoteOK", value="remoteok" in platforms)

        selected_platforms = []
        if use_linkedin:
            selected_platforms.append("linkedin")
        if use_infojobs:
            selected_platforms.append("infojobs")
        if use_remoteok:
            selected_platforms.append("remoteok")

        st.session_state.config.job_search.platforms = selected_platforms

        st.markdown("---")

        # Notificaciones
        st.subheader("🔔 Notificaciones")

        notify_telegram = st.checkbox("Telegram", value=False)
        notify_notion = st.checkbox("Notion", value=False)

        st.session_state.config.job_search.notify_telegram = notify_telegram
        st.session_state.config.job_search.notify_notion = notify_notion

    # Indicadores de estado de autenticación
    render_auth_status_indicator()


def render_stack_section():
    """Renderiza la sección de stack tecnológico"""
    st.header("🛠️ Stack Tecnológico")

    # Tabs para diferentes métodos de extracción
    tab_upload, tab_linkedin, tab_github, tab_manual = st.tabs([
        "📄 Subir CV",
        "🔵 Desde LinkedIn",
        "🐙 Desde GitHub",
        "✏️ Manual"
    ])

    with tab_upload:
        st.subheader("Sube tu CV/Portfolio")
        st.markdown("Sube tu CV en PDF, DOCX o TXT y extraeremos automáticamente las tecnologías")

        uploaded_file = st.file_uploader(
            "Selecciona tu CV",
            type=['pdf', 'docx', 'txt'],
            help="Formatos soportados: PDF, DOCX, TXT"
        )

        if uploaded_file is not None:
            # Mostrar info del archivo
            st.info(f"📄 Archivo: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

            if st.button("🔍 Extraer Stack del CV", type="primary"):
                with st.spinner("Analizando tu CV..."):
                    try:
                        # Leer contenido del archivo
                        file_content = uploaded_file.read()
                        file_extension = uploaded_file.name.split('.')[-1].lower()

                        # Extraer tecnologías
                        result = extract_stack_from_cv(file_content, file_extension)

                        # Guardar en session state
                        st.session_state.extracted_stack = result['all']

                        # Integrar en el perfil unificado
                        st.session_state.user_profile.merge_from_cv(result)

                        # Mostrar resultados
                        st.success(f"✅ Extraídas {result['count']} tecnologías!")

                        # Mostrar por categorías
                        with st.expander("Ver por categorías"):
                            for category, techs in result['categorized'].items():
                                if techs:
                                    st.markdown(f"**{category.replace('_', ' ').title()}:** {', '.join(techs)}")

                        st.balloons()
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error procesando el archivo: {e}")
                        st.info("💡 Tip: Si el archivo tiene problemas, prueba guardarlo como TXT")

    with tab_linkedin:
        st.subheader("Extraer desde LinkedIn")
        st.markdown("Extrae tecnologías automáticamente desde tu perfil de LinkedIn")

        # Verificar autenticación
        linkedin_auth = LinkedInAuth()
        if not linkedin_auth.has_valid_session():
            st.warning("⚠️ Necesitas autenticarte primero")
            st.info("👉 Ve al tab '🔐 Autenticación' para hacer login en LinkedIn")
        else:
            st.success("✅ Autenticado en LinkedIn")

            linkedin_url = st.text_input(
                "URL de tu perfil de LinkedIn",
                placeholder="https://www.linkedin.com/in/tu-perfil"
            )

            if st.button("🔍 Extraer desde LinkedIn", type="primary"):
                if linkedin_url:
                    with st.spinner("Extrayendo tecnologías de LinkedIn..."):
                        try:
                            extractor = StackExtractor()
                            result = asyncio.run(extractor.extract_from_linkedin(
                                linkedin_url=linkedin_url,
                                use_auth=True
                            ))
                            st.session_state.extracted_stack = result

                            # Integrar en el perfil unificado
                            linkedin_data = {"technologies": result}
                            st.session_state.user_profile.merge_from_linkedin(linkedin_data)
                            st.session_state.user_profile.linkedin_url = linkedin_url

                            st.success(f"✅ Extraídas {len(result)} tecnologías!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ Ingresa la URL de tu perfil")

    with tab_github:
        st.subheader("Extraer desde GitHub con Navegación Inteligente 🤖")
        st.markdown("Usa IA para navegar por tu perfil y extraer métricas profundas: contribuciones, actividad, proyectos, y más")

        github_url = st.text_input(
            "URL de tu perfil de GitHub",
            placeholder="https://github.com/tu-usuario",
            help="El sistema navegará por tu perfil para extraer información completa"
        )

        # Opción de método de extracción
        extraction_method = st.radio(
            "Método de extracción:",
            ["🤖 Navegación con IA (Recomendado)", "⚡ API Rápida (Básica)"],
            help="La navegación con IA extrae mucha más información pero tarda más"
        )

        if st.button("🔍 Extraer desde GitHub", type="primary"):
            if github_url:
                use_browser = "Navegación con IA" in extraction_method

                if use_browser:
                    with st.spinner("🤖 Navegando por tu perfil de GitHub con IA... Esto puede tardar 1-2 minutos"):
                        try:
                            # Usar browser-use para extracción profunda
                            github_data = asyncio.run(extract_github_profile_browser(github_url))

                            if github_data:
                                # Combinar tecnologías extraídas
                                all_tech = []

                                # Lenguajes
                                if github_data.get("languages"):
                                    if isinstance(github_data["languages"], list):
                                        for lang in github_data["languages"]:
                                            if isinstance(lang, dict):
                                                all_tech.append(lang.get("language"))
                                            else:
                                                all_tech.append(lang)

                                # Tecnologías y frameworks
                                if github_data.get("technologies"):
                                    all_tech.extend(github_data["technologies"])
                                if github_data.get("frameworks"):
                                    all_tech.extend(github_data["frameworks"])

                                all_tech = [t for t in all_tech if t]  # Filtrar None
                                st.session_state.extracted_stack.extend(all_tech)
                                st.session_state.extracted_stack = list(set(st.session_state.extracted_stack))

                                # Integrar en el perfil unificado
                                st.session_state.user_profile.merge_from_github(github_data)

                                # Mostrar resultados detallados
                                st.success(f"✅ Perfil extraído con éxito!")

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("### 👤 Información Básica")
                                    if github_data.get('name'):
                                        st.write(f"**Nombre:** {github_data['name']}")
                                    if github_data.get('bio'):
                                        st.write(f"**Bio:** {github_data['bio']}")
                                    if github_data.get('location'):
                                        st.write(f"**Ubicación:** {github_data['location']}")
                                    if github_data.get('company'):
                                        st.write(f"**Empresa:** {github_data['company']}")

                                    st.markdown("### 📊 Estadísticas")
                                    if github_data.get('public_repos'):
                                        st.metric("Repositorios", github_data['public_repos'])
                                    if github_data.get('followers'):
                                        st.metric("Seguidores", github_data['followers'])
                                    if github_data.get('contributions_last_year'):
                                        st.metric("Contribuciones (último año)", github_data['contributions_last_year'])

                                with col2:
                                    st.markdown("### 💻 Stack Técnico")

                                    if github_data.get('languages'):
                                        st.markdown("**🔤 Lenguajes:**")
                                        for lang in github_data['languages'][:5]:
                                            if isinstance(lang, dict):
                                                st.write(f"• {lang.get('language')} ({lang.get('percentage', 0)}%)")
                                            else:
                                                st.write(f"• {lang}")

                                    if github_data.get('frameworks'):
                                        st.markdown("**🛠️ Frameworks:**")
                                        st.write(", ".join(github_data['frameworks'][:8]))

                                    if github_data.get('activity_level'):
                                        st.markdown(f"**📈 Nivel de actividad:** {github_data['activity_level']}")

                                    if github_data.get('specializations'):
                                        st.markdown("**🎯 Especializaciones:**")
                                        st.write(", ".join(github_data['specializations']))

                                # Proyectos destacados
                                if github_data.get('repositories'):
                                    with st.expander("⭐ Proyectos Destacados"):
                                        for proj in github_data['repositories'][:5]:
                                            st.markdown(f"### {proj.get('name')} ({proj.get('stars', 0)} ⭐)")
                                            if proj.get('description'):
                                                st.write(proj['description'])
                                            if proj.get('language'):
                                                st.caption(f"Lenguaje: {proj['language']}")
                                            if proj.get('topics'):
                                                st.caption(f"Topics: {', '.join(proj['topics'][:5])}")
                                            st.markdown("---")

                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ No se pudo extraer información del perfil")

                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                            st.info("💡 Intenta con el método API Rápida si la navegación falla")

                else:
                    # Usar API rápida (método anterior)
                    with st.spinner("⚡ Extrayendo desde API de GitHub..."):
                        try:
                            github_data = extract_github_profile(github_url)

                            if github_data:
                                # Combinar tecnologías extraídas
                                all_tech = github_data.get("technologies", []) + github_data.get("top_languages", [])
                                st.session_state.extracted_stack.extend(all_tech)
                                st.session_state.extracted_stack = list(set(st.session_state.extracted_stack))

                                # Integrar en el perfil unificado
                                st.session_state.user_profile.merge_from_github(github_data)

                                # Mostrar resultados
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.success(f"✅ Perfil extraído: {github_data.get('name', 'N/A')}")
                                    st.info(f"📊 Repos públicos: {github_data.get('public_repos', 0)}")
                                    st.info(f"⭐ Seguidores: {github_data.get('followers', 0)}")

                                with col2:
                                    if github_data.get('top_languages'):
                                        st.markdown("**🔤 Lenguajes principales:**")
                                        st.write(", ".join(github_data['top_languages'][:5]))

                                    if github_data.get('technologies'):
                                        st.markdown("**🛠️ Tecnologías detectadas:**")
                                        st.write(", ".join(github_data['technologies'][:8]))

                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ No se pudo extraer información del perfil")

                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                            st.info("💡 Verifica que la URL sea correcta y que el perfil sea público")
            else:
                st.warning("⚠️ Ingresa la URL de tu perfil de GitHub")

    with tab_manual:
        st.subheader("Agregar tecnologías manualmente")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Mostrar stack actual
            if st.session_state.extracted_stack:
                st.success(f"✅ {len(st.session_state.extracted_stack)} tecnologías")
                st.write(", ".join(st.session_state.extracted_stack))
            else:
                st.info("No hay tecnologías agregadas aún")

        with col2:
            # Opción para agregar manualmente
            new_tech = st.text_input(
                "Agregar tecnología",
                placeholder="ej: Python, React, Docker"
            )
            if st.button("➕ Agregar"):
                if new_tech:
                    techs = [t.strip() for t in new_tech.split(",")]
                    st.session_state.extracted_stack.extend(techs)
                    st.session_state.extracted_stack = list(set(st.session_state.extracted_stack))
                    st.rerun()

    # Editor de stack
    with st.expander("✏️ Editar Stack"):
        edited_stack = st.text_area(
            "Edita tu stack (una tecnología por línea)",
            value="\n".join(st.session_state.extracted_stack),
            height=200
        )

        if st.button("💾 Guardar cambios"):
            st.session_state.extracted_stack = [
                t.strip() for t in edited_stack.split("\n") if t.strip()
            ]
            st.success("✅ Stack actualizado")
            st.rerun()

    # Guardar en configuración
    st.session_state.config.job_search.tech_stack = st.session_state.extracted_stack

    st.markdown("---")

    # Analizador de perfil y sugerencias automáticas
    profile = st.session_state.user_profile

    # Si hay datos del perfil, analizarlo
    if profile.technologies or profile.languages:
        st.markdown("---")
        st.header("🎯 Tu Perfil Ideal")

        # Analizar perfil
        analysis = analyze_profile_and_suggest(profile)

        # Mostrar sugerencias de roles
        st.subheader("🚀 Roles Recomendados para Ti")

        if analysis['suggested_roles']:
            st.success(f"📊 Nivel detectado: **{analysis['level']}** | Experiencia: **{analysis['years_experience']} años**")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("**Roles que mejor se adaptan a tu perfil:**")
                for idx, (role, score) in enumerate(analysis['suggested_roles'], 1):
                    st.markdown(f"{idx}. **{role}** - Match: {score}% {'🔥' if score > 70 else '⭐' if score > 50 else '✓'}")

            with col2:
                st.metric("Fortaleza del Perfil", f"{analysis['profile_strength']}/100")

            # Mostrar soft skills
            if analysis.get('soft_skills'):
                st.markdown("**💡 Soft Skills Detectadas:**")
                st.write(", ".join(analysis['soft_skills']))

            # Hard Skills
            with st.expander("🔧 Ver Hard Skills Completas"):
                hard_skills = analysis['hard_skills']
                if hard_skills['technologies']:
                    st.markdown(f"**Tecnologías:** {', '.join(hard_skills['technologies'])}")
                if hard_skills['languages']:
                    st.markdown(f"**Lenguajes:** {', '.join(hard_skills['languages'])}")
                if hard_skills['frameworks']:
                    st.markdown(f"**Frameworks:** {', '.join(hard_skills['frameworks'])}")
                if hard_skills['tools']:
                    st.markdown(f"**Herramientas:** {', '.join(hard_skills['tools'])}")

            # Queries de búsqueda sugeridas
            st.markdown("---")
            st.subheader("🔍 Búsquedas Automáticas Generadas")
            st.info("El sistema ha generado estas búsquedas basándose en tu perfil. Haz clic en cualquiera para buscar empleos:")

            # Guardar queries en session state
            if 'suggested_queries' not in st.session_state:
                st.session_state.suggested_queries = analysis['search_queries']

            col_q1, col_q2 = st.columns(2)

            with col_q1:
                for i, query in enumerate(analysis['search_queries'][:3], 1):
                    if st.button(f"🚀 Buscar: {query}", key=f"query_{i}", use_container_width=True):
                        # Navegar al tab de búsqueda y ejecutar
                        st.session_state.active_search_query = query
                        st.info(f"Búsqueda iniciada: {query}")
                        # Ejecutar búsqueda automáticamente
                        run_job_search(query)

            with col_q2:
                for i, query in enumerate(analysis['search_queries'][3:6], 4):
                    if st.button(f"🚀 Buscar: {query}", key=f"query_{i}", use_container_width=True):
                        st.session_state.active_search_query = query
                        st.info(f"Búsqueda iniciada: {query}")
                        run_job_search(query)

        else:
            st.warning("⚠️ No se pudo generar sugerencias. Completa más información en tu perfil.")

    # Mostrar perfil unificado
    with st.expander("👤 Ver Perfil Completo"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📋 Información Personal")
            if profile.name:
                st.write(f"**Nombre:** {profile.name}")
            if profile.location:
                st.write(f"**Ubicación:** {profile.location}")
            if profile.bio:
                st.write(f"**Bio:** {profile.bio}")
            if profile.current_role:
                st.write(f"**Rol actual:** {profile.current_role}")
            if profile.years_of_experience:
                st.write(f"**Experiencia:** {profile.years_of_experience} años")

            st.markdown("### 🔗 Enlaces")
            if profile.linkedin_url:
                st.write(f"[LinkedIn]({profile.linkedin_url})")
            if profile.github_url:
                st.write(f"[GitHub]({profile.github_url})")
            if profile.portfolio_url:
                st.write(f"[Portfolio]({profile.portfolio_url})")

        with col2:
            st.markdown("### 💻 Stack Tecnológico")
            if profile.technologies:
                st.write(f"**Tecnologías:** {', '.join(profile.technologies[:15])}")
            if profile.languages:
                st.write(f"**Lenguajes:** {', '.join(profile.languages[:8])}")

            st.markdown("### 📂 Fuentes de Datos")
            for source, status in profile.sources.items():
                st.write(f"✅ {source.upper()}: {status}")

        # Contexto de búsqueda
        st.markdown("### 🔍 Contexto de Búsqueda Generado")
        st.info(profile.generate_search_context())

        # Opción para guardar perfil
        if st.button("💾 Guardar Perfil"):
            profile.save()
            st.success("✅ Perfil guardado exitosamente!")

    st.markdown("---")


def render_filters_section():
    """Renderiza la sección de filtros"""
    st.header("🎯 Filtros Avanzados")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("❌ Palabras Tóxicas")
        toxic_text = st.text_area(
            "Palabras a filtrar (una por línea)",
            value="\n".join(st.session_state.config.job_search.toxic_keywords),
            height=150,
            help="Ofertas que contengan estas palabras serán descartadas automáticamente"
        )
        toxic_keywords = [k.strip() for k in toxic_text.split("\n") if k.strip()]
        st.session_state.config.job_search.toxic_keywords = toxic_keywords

    with col2:
        st.subheader("💰 Salario Mínimo")
        min_salary = st.number_input(
            "Salario mínimo anual (€)",
            min_value=0,
            max_value=200000,
            value=st.session_state.config.job_search.min_salary or 0,
            step=5000,
            help="Filtrar ofertas con salario menor (0 = sin filtro)"
        )
        if min_salary > 0:
            st.session_state.config.job_search.min_salary = min_salary
        else:
            st.session_state.config.job_search.min_salary = None

    st.markdown("---")


def render_search_section():
    """Renderiza la sección de búsqueda"""
    st.header("🔍 Búsqueda de Empleos")

    # Verificar si hay perfil
    profile = st.session_state.user_profile
    has_profile = profile.technologies or profile.languages

    if has_profile:
        # Mostrar búsquedas automáticas generadas
        analysis = analyze_profile_and_suggest(profile)

        if analysis.get('suggested_roles'):
            st.success("✨ El sistema ha analizado tu perfil y generó búsquedas automáticas!")

            st.markdown("### 🚀 Búsquedas Automáticas Recomendadas")
            st.info("Haz clic en cualquier búsqueda para encontrar empleos perfectos para ti:")

            # Mostrar queries sugeridas
            cols = st.columns(2)
            for idx, query in enumerate(analysis['search_queries'][:6]):
                col_idx = idx % 2
                with cols[col_idx]:
                    if st.button(f"🎯 {query}", key=f"auto_search_{idx}", use_container_width=True):
                        with st.spinner(f"Buscando {query}..."):
                            run_job_search(query)

            st.markdown("---")

    # Búsqueda manual (opcional)
    with st.expander("🔧 Búsqueda Manual (Opcional)"):
        st.markdown("Si prefieres buscar manualmente, puedes hacerlo aquí:")

        search_query = st.text_input(
            "Término de búsqueda manual",
            placeholder="ej: Python Developer, Full Stack Engineer, DevOps",
            help="Escribe tu propia búsqueda personalizada"
        )

        if st.button("🚀 Buscar Manualmente", type="secondary", use_container_width=True):
            if not st.session_state.extracted_stack:
                st.error("❌ Primero extrae o agrega tu stack tecnológico")
                return

            if not search_query:
                st.error("❌ Ingresa un término de búsqueda")
                return

            if not st.session_state.config.job_search.platforms:
                st.error("❌ Selecciona al menos una plataforma en la barra lateral")
                return

            # Ejecutar búsqueda
            run_job_search(search_query)


def run_job_search(search_query: str):
    """Ejecuta la búsqueda de empleos en todas las plataformas seleccionadas"""
    config = st.session_state.config.job_search
    platforms = config.platforms

    # Generar contexto enriquecido del perfil
    profile_context = st.session_state.user_profile.generate_search_context()

    # Combinar query con contexto del perfil
    enriched_query = f"{search_query}"
    if profile_context:
        enriched_query += f"\n\nContexto del candidato:\n{profile_context}"

    st.info(f"🔎 Buscando en {len(platforms)} plataforma(s)...")

    # Mostrar contexto enriquecido
    with st.expander("🧠 Query Enriquecida con tu Perfil"):
        st.text(enriched_query)

    all_jobs = {}

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, platform in enumerate(platforms):
        status_text.text(f"Buscando en {platform.upper()}...")

        try:
            if platform == "linkedin":
                scraper = LinkedInScraper()
                jobs = asyncio.run(scraper.scrape(
                    search_query=enriched_query,
                    location=config.location,
                    max_results=config.max_results_per_platform,
                    remote_only=config.remote_only,
                    published_within_days=config.published_within_days
                ))
            elif platform == "infojobs":
                scraper = InfoJobsScraper()
                jobs = asyncio.run(scraper.scrape(
                    search_query=enriched_query,
                    location=config.location,
                    max_results=config.max_results_per_platform,
                    remote_only=config.remote_only
                ))
            elif platform == "remoteok":
                scraper = RemoteOKScraper()
                jobs = asyncio.run(scraper.scrape(
                    search_query=enriched_query,
                    max_results=config.max_results_per_platform,
                    location_filter="Europe"
                ))
            else:
                jobs = []

            # Agregar plataforma a cada job
            for job in jobs:
                job['platform'] = platform

            all_jobs[platform] = jobs
            st.success(f"✅ {platform.upper()}: {len(jobs)} ofertas encontradas")

        except Exception as e:
            st.error(f"❌ Error en {platform}: {e}")
            all_jobs[platform] = []

        progress_bar.progress((idx + 1) / len(platforms))

    status_text.text("✅ Búsqueda completada")

    # Guardar resultados
    st.session_state.search_results = all_jobs

    # Filtrar resultados
    filter_jobs(all_jobs)


def filter_jobs(jobs_by_platform: Dict[str, List[Dict]]):
    """Filtra las ofertas encontradas"""
    config = st.session_state.config.job_search

    st.info("🎯 Aplicando filtros...")

    # Combinar todas las ofertas
    all_jobs = []
    for platform, jobs in jobs_by_platform.items():
        all_jobs.extend(jobs)

    # Aplicar filtros
    results = JobFilter.filter_jobs_batch(
        jobs=all_jobs,
        tech_stack=config.tech_stack,
        toxic_keywords=config.toxic_keywords,
        min_salary=config.min_salary,
        min_score=60.0
    )

    st.session_state.filtered_jobs = results['passed']

    # Mostrar estadísticas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total encontradas", results['stats']['total'])
    with col2:
        st.metric("Aprobadas", results['stats']['passed'], delta="✅")
    with col3:
        st.metric("Rechazadas", results['stats']['rejected'], delta="❌")

    st.success(f"✨ Tasa de aprobación: {results['stats']['pass_rate']}")

    # Enviar notificaciones si están habilitadas
    send_notifications(results['passed'])


def send_notifications(jobs: List[Dict]):
    """Envía notificaciones de las ofertas filtradas"""
    config = st.session_state.config

    if not jobs:
        return

    # Telegram
    if config.job_search.notify_telegram:
        if config.notifications.telegram_bot_token and config.notifications.telegram_chat_id:
            try:
                notifier = TelegramNotifier(
                    config.notifications.telegram_bot_token,
                    config.notifications.telegram_chat_id
                )
                sent = asyncio.run(notifier.send_jobs_batch(jobs))
                st.success(f"✅ {sent} ofertas enviadas a Telegram")
            except Exception as e:
                st.error(f"❌ Error enviando a Telegram: {e}")
        else:
            st.warning("⚠️ Configura TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env")

    # Notion
    if config.job_search.notify_notion:
        if config.notifications.notion_token and config.notifications.notion_database_id:
            try:
                notifier = NotionNotifier(
                    config.notifications.notion_token,
                    config.notifications.notion_database_id
                )
                added = notifier.add_jobs_batch(jobs)
                st.success(f"✅ {added} ofertas agregadas a Notion")
            except Exception as e:
                st.error(f"❌ Error agregando a Notion: {e}")
        else:
            st.warning("⚠️ Configura NOTION_TOKEN y NOTION_DATABASE_ID en .env")


def render_results_section():
    """Renderiza la sección de resultados"""
    if not st.session_state.filtered_jobs:
        st.info("👆 Realiza una búsqueda para ver resultados")
        return

    st.header("📋 Resultados Filtrados")

    jobs = st.session_state.filtered_jobs

    # Ordenar por score
    jobs_sorted = sorted(jobs, key=lambda x: x.get('filter_score', 0), reverse=True)

    # Mostrar ofertas
    for idx, job in enumerate(jobs_sorted, 1):
        with st.expander(f"#{idx} - {job.get('title', 'Sin título')} - ⭐ {job.get('filter_score', 0):.0f}/100"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**🏢 Empresa:** {job.get('company', 'N/A')}")
                st.markdown(f"**📍 Ubicación:** {job.get('location', 'N/A')}")
                st.markdown(f"**🌐 Plataforma:** {job.get('platform', 'N/A').upper()}")

                if job.get('salary'):
                    st.markdown(f"**💰 Salario:** {job['salary']}")

                if job.get('description'):
                    st.markdown(f"**📄 Descripción:** {job['description'][:200]}...")

                if job.get('filter_reasons'):
                    st.markdown(f"**✅ Razones:** {', '.join(job['filter_reasons'][:2])}")

            with col2:
                st.metric("Score", f"{job.get('filter_score', 0):.0f}/100")

                if job.get('url'):
                    st.link_button("🔗 Ver Oferta", job['url'], use_container_width=True)

    # Botón para descargar resultados
    st.download_button(
        label="💾 Descargar resultados (JSON)",
        data=json.dumps(jobs_sorted, indent=2, ensure_ascii=False),
        file_name="devjobscout_results.json",
        mime="application/json"
    )


def main():
    """Función principal de la aplicación"""
    init_session_state()

    render_header()
    render_sidebar()

    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔐 Autenticación",
        "🛠️ Stack Tecnológico",
        "🎯 Filtros",
        "🔍 Búsqueda",
        "📊 Resultados"
    ])

    with tab1:
        render_auth_section()

    with tab2:
        render_stack_section()

    with tab3:
        render_filters_section()

    with tab4:
        render_search_section()

    with tab5:
        render_results_section()


if __name__ == "__main__":
    main()
