# 💼 DevJobScout

**Tu asistente inteligente para búsqueda de empleo automatizada**

DevJobScout es una herramienta avanzada de IA que automatiza completamente tu búsqueda de empleo. Extrae tu perfil profesional desde múltiples fuentes (CV, GitHub, LinkedIn), analiza automáticamente tus skills, sugiere roles ideales y busca las mejores ofertas en LinkedIn, InfoJobs y RemoteOK.

## ✨ Características Principales

### 🎯 Extracción Inteligente de Perfil
- **📄 Parser de CV avanzado**: Extrae tecnologías, experiencia, roles y empresas desde PDF, TXT o DOCX
- **🐙 Extracción profunda de GitHub**: Navega tu perfil con IA para obtener:
  - Lenguajes principales con porcentajes
  - Repositorios destacados con estrellas
  - Contribuciones del último año
  - Frameworks y herramientas inferidas
  - Nivel de actividad y especializaciones
- **💼 Extracción de LinkedIn**: Stack tecnológico y experiencia profesional
- **🔗 Perfil unificado**: Combina toda la información en un único perfil enriquecido

### 🤖 Análisis Automático con IA
- **🎓 Detección automática de nivel**: Junior, Mid-Level o Senior
- **💡 Sugerencia de roles ideales**: Basado en tu stack completo
- **📊 Scoring de fortaleza del perfil**: Evalúa la completitud de tu perfil (0-100)
- **🔍 Generación de queries optimizadas**: Búsquedas automáticas personalizadas
- **🎯 Soft skills detection**: Extrae habilidades blandas de tu bio

### 🌐 Scraping Multi-Plataforma
- **🔵 LinkedIn**: Búsqueda con filtros avanzados y autenticación persistente
- **🟠 InfoJobs**: Scraping de ofertas con filtros personalizables
- **🟢 RemoteOK**: Enfocado en trabajos 100% remotos
- **🤖 Browser-use**: Navegación autónoma con visión por computadora

### 🎯 Filtrado Inteligente
- **✅ Match con tech stack**: Puntuación basada en coincidencias
- **❌ Detección de red flags**: Filtra "rockstar", "ninja", "fast-paced", etc.
- **💰 Filtro de salario**: Establece tu mínimo aceptable
- **📍 Preferencias de ubicación**: Remote, híbrido o presencial
- **🏆 Sistema de scoring 0-100**: Solo ves las mejores oportunidades

### 🔔 Notificaciones Automáticas
- **📱 Telegram**: Alertas instantáneas de nuevas ofertas
- **📝 Notion**: Guarda ofertas automáticamente en tu workspace
- **📊 Dashboard**: Visualización completa en interfaz web

### 🖥️ Interfaz Completa
- **🎨 UI moderna con Streamlit**: Fácil de usar
- **🔐 Gestión de autenticación**: Login manual persistente
- **📈 Visualización de resultados**: Ordenados por relevancia
- **💾 Exportación de datos**: JSON, CSV y más

## 🚀 Instalación Rápida

### Requisitos Previos

- **Python 3.11+**
- **[uv](https://github.com/astral-sh/uv)** (gestor de paquetes rápido)
- **Git**

### Instalación

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd devjobscout

# Instalar dependencias
uv sync

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tu API key de browser-use
```

## ⚙️ Configuración

### 1. Variables de Entorno

Edita el archivo `.env` con tus credenciales:

```bash
# Browser-use API Key (OBLIGATORIO)
# Obtén tu key en: https://browser-use.com
BROWSER_USE_API_KEY=tu_api_key_aqui

# Telegram (OPCIONAL - para notificaciones)
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id

# Notion (OPCIONAL - para guardar ofertas)
NOTION_TOKEN=tu_notion_token
NOTION_DATABASE_ID=tu_database_id
```

### 2. Autenticación de Plataformas

LinkedIn requiere autenticación para acceder a ofertas. DevJobScout incluye un sistema de login manual con persistencia de sesión.

#### Opción A - Desde la interfaz web:
```bash
./run.sh  # o: uv run streamlit run app.py
```
1. Ve al tab **"🔐 Autenticación"**
2. Haz clic en "Login Manual LinkedIn"
3. Se abre un navegador real donde haces login normalmente
4. La sesión se guarda en `sessions/linkedin_session.json`

#### Opción B - Desde línea de comandos:
```bash
uv run python src/auth/linkedin_auth.py
```

**📖 Guía completa de autenticación**: [AUTH_GUIDE.md](AUTH_GUIDE.md)

### 3. Configurar Notificaciones (Opcional)

#### Telegram
1. Habla con [@BotFather](https://t.me/botfather) → `/newbot`
2. Guarda el token
3. Obtén tu Chat ID con [@userinfobot](https://t.me/userinfobot)
4. Agrégalos al `.env`

#### Notion
1. Crea integración en [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Copia el token
3. Crea base de datos y compártela con la integración
4. Copia el Database ID (de la URL)
5. Agrégalos al `.env`

## 🎮 Guía de Uso

### Interfaz Web (Recomendado)

```bash
cd devjobscout
./run.sh
# Se abre automáticamente en http://localhost:8501
```

#### Flujo de Trabajo Completo

**Paso 1: Construir tu Perfil** (Tab "📊 Perfil")

1. **Sube tu CV**:
   - Formatos soportados: PDF, TXT, DOCX
   - Extrae: tecnologías, experiencia, roles, empresas, contacto

2. **Extrae de GitHub**:
   - Ingresa tu URL de GitHub (ej: `https://github.com/username`)
   - Extrae automáticamente:
     - Lenguajes principales con %
     - Top repos con estrellas
     - Contribuciones último año
     - Frameworks/herramientas inferidas
     - Nivel de actividad

3. **Extrae de LinkedIn** (opcional):
   - Requiere autenticación previa
   - Complementa info profesional

4. **Revisa el Perfil Unificado**:
   - Ve toda tu info consolidada
   - Edita manualmente si es necesario
   - El sistema genera un contexto enriquecido automáticamente

**Paso 2: Análisis Automático** (Tab "🎯 Análisis")

El sistema analiza tu perfil y te muestra:

- **Nivel detectado**: Junior / Mid-Level / Senior
- **Roles sugeridos**: Top 5 con score de match
- **Años de experiencia**: Calculados o estimados
- **Tech stack categorizado**: Lenguajes, frameworks, tools
- **Soft skills**: Extraídas de tu bio
- **Queries optimizadas**: Búsquedas recomendadas
- **Fortaleza del perfil**: Score 0-100

**Paso 3: Configurar Filtros** (Tab "🔧 Filtros")

- **Palabras tóxicas**: Por defecto incluye "rockstar", "ninja", etc.
- **Salario mínimo**: Define tu expectativa
- **Keywords obligatorias**: Tecnologías que DEBEN estar
- **Preferencias de ubicación**: Remote, híbrido, presencial

**Paso 4: Buscar Empleos** (Tab "🔍 Búsqueda")

1. Selecciona plataformas: LinkedIn, InfoJobs, RemoteOK
2. Usa las queries sugeridas o escribe tu propia búsqueda
3. El sistema enriquece la búsqueda con tu perfil completo
4. Haz clic en "Buscar Empleos"
5. Espera mientras los agentes navegan las plataformas

**Paso 5: Revisar Resultados** (Tab "📋 Resultados")

- **Ofertas aprobadas**: Score ≥ 60/100
- **Ofertas rechazadas**: Con razón del rechazo
- **Ordenadas por relevancia**: Mejor match primero
- **Exportar**: JSON, CSV
- **Notificaciones automáticas**: Si configuraste Telegram/Notion

### Uso Programático

#### 1. Extraer y Analizar Perfil Completo

```python
from src.extractors.cv_parser import extract_stack_from_cv
from src.extractors.github_browser_extractor import extract_github_profile_browser
from src.profile.user_profile import UserProfile
from src.profile.profile_analyzer import analyze_profile_and_suggest
import asyncio

async def construir_perfil():
    # 1. Extraer desde CV
    with open('mi_cv.pdf', 'rb') as f:
        cv_data = extract_stack_from_cv(f.read(), 'pdf')

    # 2. Extraer desde GitHub
    github_data = await extract_github_profile_browser('https://github.com/username')

    # 3. Crear perfil unificado
    profile = UserProfile()
    profile.merge_from_cv(cv_data)
    profile.merge_from_github(github_data)

    # 4. Analizar y obtener sugerencias
    analysis = analyze_profile_and_suggest(profile)

    print(f"Nivel: {analysis['level']}")
    print(f"Roles sugeridos: {analysis['suggested_roles']}")
    print(f"Fortaleza del perfil: {analysis['profile_strength']}/100")

    # 5. Guardar perfil
    profile.save('src/data/user_profile.json')

    return profile, analysis

profile, analysis = asyncio.run(construir_perfil())
```

#### 2. Buscar con Contexto Enriquecido

```python
from src.scrapers.linkedin_agent_v2 import LinkedInScraper
from src.profile.user_profile import UserProfile
import asyncio

async def buscar_con_perfil():
    # Cargar perfil
    profile = UserProfile.load('src/data/user_profile.json')

    # Generar contexto enriquecido
    context = profile.generate_search_context()

    # Buscar en LinkedIn con contexto
    scraper = LinkedInScraper()
    jobs = await scraper.scrape(
        search_query="Senior Backend Developer",
        location="Spain",
        max_results=20,
        remote_only=True,
        enriched_context=context  # ← Mejora la precisión
    )

    return jobs

jobs = asyncio.run(buscar_con_perfil())
```

#### 3. Filtrar y Notificar

```python
from src.filters.job_filter import JobFilter
from src.notifiers.telegram_notifier import notify_jobs_telegram
import asyncio

# Filtrar con tu tech stack
results = JobFilter.filter_jobs_batch(
    jobs=jobs,
    tech_stack=["Python", "Django", "Docker", "AWS"],
    toxic_keywords=["rockstar", "ninja"],
    min_salary=50000,
    required_keywords=["Python", "backend"]
)

# Notificar a Telegram
approved = results['passed']
asyncio.run(notify_jobs_telegram(
    bot_token="tu_token",
    chat_id="tu_chat_id",
    jobs=approved[:5]  # Top 5
))

print(f"✅ Aprobadas: {len(approved)}")
print(f"❌ Rechazadas: {len(results['rejected'])}")
```

#### 4. Pipeline Completo Automatizado

```python
from src.profile.user_profile import UserProfile
from src.profile.profile_analyzer import analyze_profile_and_suggest
from src.scrapers.linkedin_agent_v2 import LinkedInScraper
from src.scrapers.infojobs_agent import InfoJobsScraper
from src.filters.job_filter import JobFilter
from src.notifiers.telegram_notifier import notify_jobs_telegram
import asyncio

async def pipeline_completo():
    # 1. Cargar perfil
    profile = UserProfile.load('src/data/user_profile.json')

    # 2. Analizar y obtener sugerencias
    analysis = analyze_profile_and_suggest(profile)

    print(f"🎯 Nivel: {analysis['level']}")
    print(f"💼 Top rol sugerido: {analysis['suggested_roles'][0][0]}")

    # 3. Usar queries optimizadas automáticamente
    queries = analysis['search_queries']

    all_jobs = []

    # 4. Buscar en múltiples plataformas
    for query in queries[:2]:  # Top 2 queries
        print(f"🔍 Buscando: {query}")

        # LinkedIn
        linkedin_scraper = LinkedInScraper()
        linkedin_jobs = await linkedin_scraper.scrape(
            search_query=query,
            location="Remote",
            max_results=10,
            enriched_context=profile.generate_search_context()
        )
        all_jobs.extend(linkedin_jobs)

        # InfoJobs
        infojobs_scraper = InfoJobsScraper()
        infojobs_jobs = await infojobs_scraper.scrape(
            search_query=query,
            location="España",
            max_results=10
        )
        all_jobs.extend(infojobs_jobs)

    # 5. Filtrar inteligentemente
    tech_stack = profile.technologies + profile.languages + profile.frameworks

    results = JobFilter.filter_jobs_batch(
        jobs=all_jobs,
        tech_stack=tech_stack[:20],  # Top 20 techs
        toxic_keywords=["rockstar", "ninja", "fast-paced"],
        min_salary=40000
    )

    approved = results['passed']

    # 6. Ordenar por score
    approved_sorted = sorted(approved, key=lambda x: x.get('score', 0), reverse=True)

    # 7. Notificar top ofertas
    if approved_sorted:
        await notify_jobs_telegram(
            bot_token="tu_token",
            chat_id="tu_chat_id",
            jobs=approved_sorted[:10]
        )

    print(f"\n✅ Pipeline completado:")
    print(f"   📊 Total escaneadas: {len(all_jobs)}")
    print(f"   ✅ Aprobadas: {len(approved)}")
    print(f"   ❌ Rechazadas: {len(results['rejected'])}")
    print(f"   🏆 Mejor score: {approved_sorted[0]['score'] if approved_sorted else 0}")

    return approved_sorted

# Ejecutar
jobs = asyncio.run(pipeline_completo())
```

## 📁 Arquitectura del Proyecto

```
devjobscout/
├── app.py                          # 🎨 Aplicación Streamlit principal
├── run.sh                          # 🚀 Script de inicio rápido
├── pyproject.toml                  # 📦 Dependencias y configuración
├── .env                            # 🔐 Variables de entorno (no versionado)
├── .env.example                    # 📋 Template de variables
├── .gitignore                      # 🚫 Archivos ignorados
│
├── src/
│   ├── config/
│   │   └── settings.py             # ⚙️ Configuración centralizada
│   │
│   ├── auth/                       # 🔐 Sistema de autenticación
│   │   ├── linkedin_auth.py        # Login manual LinkedIn con Playwright
│   │   ├── google_auth.py          # Login Google Drive (futuro)
│   │   └── session_manager.py      # Gestión de sesiones persistentes
│   │
│   ├── extractors/                 # 📤 Extractores de información
│   │   ├── cv_parser.py            # Parser de CV (PDF/TXT/DOCX)
│   │   ├── github_browser_extractor.py  # Extractor GitHub con browser-use
│   │   ├── github_extractor.py     # Extractor GitHub API (legacy)
│   │   └── stack_extractor.py      # Extractor de stack (LinkedIn/Portfolio)
│   │
│   ├── profile/                    # 👤 Sistema de perfil unificado
│   │   ├── user_profile.py         # Clase UserProfile + merge logic
│   │   └── profile_analyzer.py     # Análisis y sugerencia de roles
│   │
│   ├── scrapers/                   # 🕷️ Web scrapers con browser-use
│   │   ├── linkedin_agent_v2.py    # LinkedIn con autenticación
│   │   ├── infojobs_agent.py       # InfoJobs
│   │   └── remoteok_agent.py       # RemoteOK
│   │
│   ├── filters/                    # 🎯 Sistema de filtrado
│   │   └── job_filter.py           # Filtros + scoring + toxic detection
│   │
│   ├── notifiers/                  # 🔔 Notificadores
│   │   ├── telegram_notifier.py    # Envío a Telegram
│   │   └── notion_notifier.py      # Guardado en Notion
│   │
│   ├── ui/                         # 🎨 Componentes UI
│   │   └── auth_ui.py              # UI de autenticación
│   │
│   └── data/                       # 💾 Datos persistentes
│       ├── user_profile.json       # Perfil unificado
│       ├── github_profile.json     # Datos de GitHub
│       ├── linkedin_jobs.json      # Ofertas de LinkedIn
│       ├── infojobs_jobs.json      # Ofertas de InfoJobs
│       └── remoteok_jobs.json      # Ofertas de RemoteOK
│
├── sessions/                       # 🔐 Sesiones de autenticación
│   └── linkedin_session.json       # Cookies de LinkedIn
│
├── logs/                           # 📝 Logs de browser-use
│   ├── github_browser_conversation.json/
│   ├── linkedin_conversation.json/
│   ├── infojobs_conversation.json/
│   └── remoteok_conversation.json/
│
└── docs/                           # 📚 Documentación
    ├── AUTH_GUIDE.md               # Guía de autenticación
    └── QUICKSTART.md               # Guía rápida
```

## 🧪 Testing y Debugging

### Test de Componentes Individuales

```bash
# Test CV Parser
uv run python src/extractors/cv_parser.py

# Test GitHub Extractor
uv run python src/extractors/github_browser_extractor.py https://github.com/username

# Test Profile Analyzer
uv run python src/profile/profile_analyzer.py

# Test LinkedIn Scraper
uv run python src/scrapers/linkedin_agent_v2.py

# Test InfoJobs Scraper
uv run python src/scrapers/infojobs_agent.py

# Test RemoteOK Scraper
uv run python src/scrapers/remoteok_agent.py

# Test Filtros
uv run python src/filters/job_filter.py
```

### Debugging con Logs

Browser-use guarda conversaciones detalladas en `logs/`. Para ver qué está haciendo el agente:

```bash
# Ver último log de GitHub
cat logs/github_browser_conversation.json/conversation_*.txt | tail -100

# Ver logs de LinkedIn
ls logs/linkedin_conversation.json/
```

### Modo Verbose

Activa logging detallado en `.env`:

```bash
LOG_LEVEL=DEBUG
HEADLESS=false  # Ver el navegador en acción
```

## 🤖 Cómo Funciona Browser-Use

DevJobScout usa [browser-use](https://github.com/browser-use/browser-use) v0.9.5, que permite:

1. **Control con IA**: Los agentes "ven" páginas como humanos usando visión por computadora
2. **Navegación autónoma**: Deciden qué hacer según instrucciones en lenguaje natural
3. **Herramientas custom**: Defines funciones que el agente puede llamar
4. **Persistencia**: Sesiones guardadas para evitar re-logins

**Ejemplo de agente:**

```python
from browser_use import Agent, Browser, ChatBrowserUse, Tools

tools = Tools()

@tools.action('Guarda ofertas de trabajo')
def guardar_ofertas(jobs_json: str) -> str:
    jobs = json.loads(jobs_json)
    # Procesar ofertas...
    return f"✅ Guardadas {len(jobs)} ofertas"

agent = Agent(
    task="""
    Ve a LinkedIn y busca 'Python developer remote'.
    Extrae las primeras 10 ofertas con: título, empresa, ubicación, descripción.
    Llama a guardar_ofertas con los datos en JSON.
    """,
    llm=ChatBrowserUse(),
    browser=Browser(),
    use_vision=True,
    tools=tools
)

await agent.run()
```

## 📊 Sistema de Scoring Detallado

Las ofertas se evalúan 0-100 según estos criterios:

| Criterio | Puntos | Descripción |
|----------|--------|-------------|
| **Match Tech Stack** | 0-40 | Número de tecnologías coincidentes |
| **Keywords Requeridas** | 0-20 | Si las keywords obligatorias están presentes |
| **Ubicación** | 0-15 | Coincide con preferencias |
| **Salario** | 0-15 | Cumple mínimo especificado |
| **Señales Positivas** | 0-10 | Remote, benefits, flexible, etc. |

**Penalizaciones:**
- **-20**: Contiene palabras tóxicas (rockstar, ninja, fast-paced)
- **-10**: No cumple salario mínimo
- **-5**: Ubicación no deseada

**Umbral de aprobación**: 60/100

**Ejemplo de cálculo:**

```
Oferta: "Senior Python Developer - Remote - €60k"
Tech Stack Match: 8/10 coincidencias → 32 puntos
Keywords: Tiene "Python" (requerida) → 20 puntos
Ubicación: Remote (preferida) → 15 puntos
Salario: €60k > €40k (mínimo) → 15 puntos
Señales: Remote, senior → 8 puntos
─────────────────────────────────────────────
TOTAL: 90/100 ✅ APROBADA
```

## ⚠️ Limitaciones y Consideraciones

### Técnicas
- **Rate limiting**: Las plataformas pueden limitar requests. Se recomienda delay entre búsquedas
- **Cambios en sitios**: Los sitios web cambian. Browser-use es resiliente pero puede requerir ajustes
- **Costos API**: Browser-use tiene límites según tu plan
- **Dependencia de sesiones**: LinkedIn requiere autenticación manual inicial

### Legales
- **Terms of Service**: Respeta los ToS de cada plataforma
- **Uso responsable**: No abuses de las búsquedas automatizadas
- **Privacidad**: Tus datos se guardan localmente, nunca se comparten

### Prácticas Recomendadas
- No ejecutes scraping masivo (>100 ofertas/hora)
- Usa delays razonables entre requests
- Verifica manualmente ofertas antes de aplicar
- Mantén tus sesiones seguras (no compartas `sessions/`)

## 🔧 Personalización Avanzada

### Agregar Nueva Plataforma

1. Crea scraper en `src/scrapers/nueva_plataforma.py`:

```python
from browser_use import Agent, Browser, ChatBrowserUse, Tools
import json

class NuevaPlataformaScraper:
    def __init__(self):
        self.tools = Tools()
        self._setup_tools()

    def _setup_tools(self):
        @self.tools.action('Guarda ofertas')
        def guardar_ofertas(jobs_json: str) -> str:
            jobs = json.loads(jobs_json)
            self.scraped_jobs = jobs
            return f"✅ {len(jobs)} ofertas guardadas"

    async def scrape(self, search_query: str, max_results: int = 10):
        task = f"""
        Ve a nueva-plataforma.com y busca '{search_query}'.
        Extrae {max_results} ofertas con:
        - title, company, location, salary, description, url
        Llama a guardar_ofertas con el JSON.
        """

        agent = Agent(
            task=task,
            llm=ChatBrowserUse(),
            browser=Browser(),
            use_vision=True,
            tools=self.tools
        )

        await agent.run()
        return self.scraped_jobs
```

2. Agrégalo a `app.py`:

```python
from src.scrapers.nueva_plataforma import NuevaPlataformaScraper

# En el tab de búsqueda
if st.checkbox("Nueva Plataforma"):
    scraper = NuevaPlataformaScraper()
    jobs = await scraper.scrape(query, max_results=10)
```

### Modificar Criterios de Scoring

Edita `src/filters/job_filter.py`:

```python
def filter_job(job: Dict, ...) -> Dict:
    score = 0

    # Modificar pesos
    tech_matches = len(set(tech_stack_lower) & desc_lower_set)
    score += min(tech_matches * 5, 40)  # ← Cambiar de 4 a 5

    # Agregar nuevo criterio
    if 'startup' in description.lower():
        score += 5  # Bonus para startups

    # ...
```

### Personalizar Análisis de Perfil

Edita `src/profile/profile_analyzer.py`:

```python
ROLE_PATTERNS = {
    "Tu Nuevo Rol": {
        "required": ["categoria"],
        "technologies": ["Tech1", "Tech2"],
        "min_tech_count": 2,
        "keywords": ["keyword1", "keyword2"]
    }
}
```

## 🛠️ Troubleshooting

### Problemas Comunes

#### "ModuleNotFoundError: No module named 'browser_use'"
```bash
uv sync
```

#### "Browser-use API key invalid"
Verifica que tu API key en `.env` sea correcta. Obtén una nueva en [browser-use.com](https://browser-use.com).

#### "No se extraen tecnologías del perfil"
- Verifica que la URL sea pública
- Revisa logs en `logs/github_browser_conversation.json/`
- Intenta con extracción manual desde CV

#### "LinkedIn requiere login cada vez"
La sesión puede haber expirado:
```bash
uv run python src/auth/linkedin_auth.py
```

#### "Scrapers no encuentran ofertas"
- Verifica conexión a internet
- Revisa logs de browser-use
- El sitio puede haber cambiado estructura (ajusta prompts)

#### "Score siempre bajo"
- Verifica que tu tech stack esté completo en el perfil
- Revisa los criterios de scoring en `job_filter.py`
- Puede que la oferta no coincida con tu perfil

### Logs y Debugging

```bash
# Ver últimos errores
tail -f logs/linkedin_conversation.json/conversation_*.txt

# Limpiar caché
rm -rf sessions/*.json
rm -rf src/data/*.json

# Reiniciar sesión
uv run python src/auth/linkedin_auth.py
```

## 🚀 Roadmap

### Próximas Features

- [ ] **Programación automática**: Cron jobs para búsquedas periódicas
- [ ] **Más plataformas**: Indeed, Glassdoor, AngelList, Stack Overflow Jobs
- [ ] **Base de datos local**: SQLite para tracking histórico
- [ ] **Deduplicación**: Detectar ofertas duplicadas entre plataformas
- [ ] **Tracking de aplicaciones**: Seguimiento de estado (aplicado, entrevista, rechazado)
- [ ] **Cover letters automáticas**: Generación con IA basada en oferta + perfil
- [ ] **Análisis de mercado**: Tendencias de salarios, tecnologías demandadas
- [ ] **Email scraping**: Integración con Gmail para recibir alertas
- [ ] **Chrome extension**: Analizar ofertas mientras navegas
- [ ] **API REST**: Exponer funcionalidad como servicio

### Mejoras Planificadas

- [ ] Cache inteligente de búsquedas
- [ ] Modo offline con datos guardados
- [ ] Exportación a Excel con formato
- [ ] Gráficos de análisis de mercado
- [ ] Sistema de recomendaciones ML
- [ ] Multi-idioma (EN, ES, FR)

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas!

### Cómo Contribuir

1. **Fork** el repositorio
2. **Crea una rama** para tu feature:
   ```bash
   git checkout -b feature/mi-nueva-feature
   ```
3. **Haz tus cambios** con commits descriptivos:
   ```bash
   git commit -m "feat: agrega scraper de Indeed"
   ```
4. **Push** a tu fork:
   ```bash
   git push origin feature/mi-nueva-feature
   ```
5. **Abre un Pull Request** con descripción detallada

### Áreas que Necesitan Ayuda

- **Scrapers**: Nuevas plataformas de empleo
- **Filtros**: Nuevos criterios de evaluación
- **UI**: Mejoras en la interfaz
- **Tests**: Cobertura de tests
- **Docs**: Tutoriales y guías
- **i18n**: Traducciones

## 📝 Licencia

Este proyecto es de código abierto bajo licencia **MIT**.

Puedes usar, modificar y distribuir este código libremente, siempre que mantengas el aviso de copyright original.

## 📧 Soporte y Contacto

- **Issues**: [Abre un issue](https://github.com/tu-repo/devjobscout/issues)
- **Discussions**: Para preguntas y conversaciones
- **Email**: Para consultas privadas

## 🙏 Agradecimientos

- [browser-use](https://github.com/browser-use/browser-use) - Framework de automatización con IA
- [Streamlit](https://streamlit.io) - Framework de UI
- [Playwright](https://playwright.dev) - Automatización de navegadores
- [uv](https://github.com/astral-sh/uv) - Gestor de paquetes ultrarrápido

## 📚 Recursos Adicionales

- [Guía de Autenticación](AUTH_GUIDE.md)
- [Quick Start Guide](QUICKSTART.md)
- [Browser-use Docs](https://docs.browser-use.com)
- [Streamlit Docs](https://docs.streamlit.io)

---

**Hecho con ❤️ usando IA y automatización inteligente**

**¿Te ha sido útil DevJobScout? Dale una ⭐ en GitHub!**
