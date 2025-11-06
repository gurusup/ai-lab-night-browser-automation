# Guía de Uso - Scraper de Agencias de Seguros

## Instalación rápida con Makefile

```bash
make setup    # Crear venv e instalar dependencias
make import   # Importar códigos postales
make run      # Ejecutar scraper
make view     # Ver estadísticas y últimas 10 agencias
make logs     # Ver archivos de log generados
```

## Instalación manual

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Configuración

Editar `.env` con tu API key:
```
BROWSER_USE_API_KEY=tu_clave_aquí
OPENAI_API_KEY=tu_clave_openai
```

## Uso

### 1. Importar códigos postales (primera vez)

```bash
make import
# o manualmente:
venv/bin/python import_postcodes.py
```

Descarga ~11,000 códigos postales de España desde fuente oficial INE.

### 2. Ejecutar scraper

**Con Makefile:**
```bash
make run
```

**Modo continuo** (hasta completar todos):
```bash
venv/bin/python main.py
```

**Modo limitado** (N iteraciones):
```bash
venv/bin/python main.py 10
```

## Características

- **Sistema anti-duplicados**: Hash MD5 de teléfono + email
- **Base de datos SQLite**: `insurance_agencies.db`
- **Auto-tracking**: Marca fecha y resultados por CP
- **Re-búsqueda automática**: Al completar todos, rebusca el más antiguo
- **Rate limiting**: Pausa de 2s entre búsquedas
- **Logging automático**: Cada ejecución guarda logs en `logs/scraper_YYYYMMDD_HHMMSS.log`

## Logs

Cada ejecución genera un archivo de log con timestamp en `logs/`:
- Ver logs disponibles: `make logs`
- Los logs incluyen toda la salida del scraper
- Formato: `logs/scraper_20251106_194729.log`

## Estructura

```
database.py          - SQLite con tracking de CPs
scraper.py           - Browser-use + Google Maps
main.py              - Procesamiento automático
import_postcodes.py  - Importación CPs desde INE
```
