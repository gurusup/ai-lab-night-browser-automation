# 🚀 Guía de Inicio Rápido - DevJobScout

## En 3 pasos:

### 1️⃣ Instalar dependencias

```bash
cd devjobscout
uv sync
```

### 2️⃣ Configurar (opcional pero recomendado)

Edita el archivo `.env` con tus credenciales:

```bash
nano .env
```

Solo necesitas la API key de browser-use (ya está incluida).
Telegram y Notion son opcionales.

### 3️⃣ Iniciar la aplicación

**Opción A - Script automático:**
```bash
./run.sh
```

**Opción B - Manual:**
```bash
uv run streamlit run app.py
```

Abre tu navegador en: **http://localhost:8501**

---

## 📖 Cómo usar la interfaz

### Paso 1: Extraer tu stack tecnológico

1. Ve a la **barra lateral** (izquierda)
2. Ingresa tu URL de LinkedIn
3. (Opcional) Ingresa URL de tu portfolio
4. Haz clic en **"Extraer Stack Tecnológico"**
5. Espera unos segundos mientras browser-use analiza tu perfil

**Tip:** También puedes agregar tecnologías manualmente en el Tab "Stack Tecnológico"

### Paso 2: Configurar filtros

1. Ve al tab **"Filtros"**
2. Revisa las palabras tóxicas predefinidas
3. Agrega más si quieres
4. Establece un salario mínimo (opcional)

### Paso 3: Buscar empleos

1. Ve al tab **"Búsqueda"**
2. Ingresa qué tipo de trabajo buscas (ej: "Python Developer")
3. Selecciona plataformas en la barra lateral
4. Configura parámetros (ubicación, remoto, días)
5. Haz clic en **"Buscar Empleos"**

### Paso 4: Revisar resultados

1. Ve al tab **"Resultados"**
2. Revisa las ofertas ordenadas por score
3. Haz clic en "Ver Oferta" para abrirlas
4. Descarga los resultados en JSON

---

## 🧪 Test rápido sin interfaz

### Probar scraper de LinkedIn:

```bash
uv run python src/scrapers/linkedin_agent_v2.py
```

### Probar scraper de InfoJobs:

```bash
uv run python src/scrapers/infojobs_agent.py
```

### Probar scraper de RemoteOK:

```bash
uv run python src/scrapers/remoteok_agent.py
```

### Probar extractor de stack:

```bash
uv run python src/extractors/stack_extractor.py
```

### Probar filtros:

```bash
uv run python src/filters/job_filter.py
```

---

## 🔧 Configuración de notificaciones

### Telegram

1. Abre Telegram
2. Habla con [@BotFather](https://t.me/botfather)
3. Envía `/newbot` y sigue las instrucciones
4. Guarda el token que te da
5. Habla con [@userinfobot](https://t.me/userinfobot) para obtener tu Chat ID
6. Agrega ambos al `.env`:
   ```
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   TELEGRAM_CHAT_ID=tu_chat_id
   ```
7. Activa "Telegram" en la barra lateral de la app

### Notion

1. Ve a [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Haz clic en "New integration"
3. Dale un nombre (ej: DevJobScout)
4. Copia el "Internal Integration Token"
5. En Notion, crea una página nueva
6. Dentro de esa página, crea una base de datos (Database - Full page)
7. Haz clic en "..." → "Add connections" → Selecciona tu integración
8. Copia el ID de la base de datos (está en la URL)
9. Agrega ambos al `.env`:
   ```
   NOTION_TOKEN=tu_token_aqui
   NOTION_DATABASE_ID=tu_database_id
   ```
10. Activa "Notion" en la barra lateral de la app

**Nota:** Puedes crear automáticamente la estructura de la base de datos con:
```bash
uv run python -c "from src.notifiers.notion_notifier import create_jobs_database_template; create_jobs_database_template('tu_token', 'id_pagina_padre')"
```

---

## ❓ Preguntas frecuentes

### ¿Es gratis?

- **Python y uv**: Sí, 100% gratis
- **browser-use**: Tiene una capa gratuita, pero puede tener costos según uso
- **Telegram**: Gratis
- **Notion**: Gratis para uso personal

### ¿Necesito cuenta en LinkedIn para scraping?

No necesariamente. browser-use puede acceder a ofertas públicas sin login. Pero algunas funciones pueden requerir autenticación.

### ¿Cuánto tiempo tarda una búsqueda?

- LinkedIn: 2-5 minutos
- InfoJobs: 2-4 minutos
- RemoteOK: 1-3 minutos

**Total para 3 plataformas**: ~10 minutos

### ¿Puedo ejecutarlo cada día automáticamente?

Sí! Puedes usar cron en Linux/Mac o Task Scheduler en Windows.

Ejemplo con cron (ejecuta cada día a las 9 AM):
```bash
0 9 * * * cd /ruta/a/devjobscout && uv run python -c "from app import run_search; run_search()"
```

### ¿Se pueden agregar más plataformas?

Sí! Crea un nuevo scraper en `src/scrapers/` siguiendo el patrón de los existentes y agrégalo a `app.py`.

---

## 🐛 Problemas comunes

### "ModuleNotFoundError"
```bash
uv sync
```

### "Port 8501 already in use"
```bash
pkill -f streamlit
```
O usa otro puerto:
```bash
uv run streamlit run app.py --server.port 8502
```

### "Browser-use API error"
Verifica tu API key en `.env`

### "No se extraen tecnologías"
- Verifica que la URL sea pública
- Prueba con extracción manual
- Revisa logs en `logs/`

---

## 📚 Recursos adicionales

- [Documentación completa](README.md)
- [Browser-use docs](https://github.com/browser-use/browser-use)
- [Streamlit docs](https://docs.streamlit.io)

---

**¿Todo listo? ¡Lanza la aplicación con `./run.sh` y empieza a buscar trabajo inteligentemente!** 🚀
