# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Sistema de scraping automatizado de agencias de seguros españolas usando browser-use (agentic browser automation). El proyecto forma parte de un experimento de AI Lab Night explorando automatización de navegadores con LLMs.

## Comandos Esenciales

```bash
make setup    # Configurar entorno virtual e instalar dependencias
make import   # Importar ~11K códigos postales de España desde INE
make run      # Ejecutar scraper en modo continuo
make view     # Ver estadísticas y últimas 10 agencias extraídas
make logs     # Listar archivos de log generados

# Ejecución manual con control de iteraciones
venv/bin/python main.py           # Modo continuo
venv/bin/python main.py 10        # Limitar a N iteraciones
```

## Arquitectura del Sistema

### Flujo de Datos Central

El sistema opera en un ciclo continuo controlado por `main.py`:

1. **Selección inteligente de CP**: `database.py::get_next_postal_code()` prioriza códigos postales nunca buscados o más antiguos, luego ordena por proximidad numérica al CP de referencia (41007)
2. **Scraping con agente LLM**: `scraper.py` usa browser-use para ejecutar un agente que navega Google Maps, extrae datos de hasta 10 agencias, y devuelve markdown estructurado
3. **Parsing de resultados**: El markdown extraído se convierte a diccionarios Python parseando tablas markdown línea por línea
4. **Persistencia con anti-duplicados**: `database.py` usa hash MD5 de teléfono+email para prevenir duplicados antes de insertar

### Sistema Anti-Duplicados

**Decisión arquitectónica crítica**: Se usa teléfono + email (no nombre + dirección) porque:
- Google Maps puede listar el mismo negocio con ligeras variaciones de nombre
- Teléfono y email son identificadores más estables
- Hash MD5 permite búsquedas rápidas vía índice único en SQLite

Implementado en `database.py::_generate_hash()` y aplicado en `insert_agency()`.

### Tracking de Progreso

Tabla `postal_codes` mantiene estado de búsqueda:
- `last_searched_at`: timestamp última búsqueda
- `results_count`: número de resultados en última búsqueda
- `total_searches`: contador de veces buscado

Permite:
- Reanudar después de interrupciones
- Re-buscar códigos postales antiguos para actualizar datos
- Métricas de cobertura geográfica

### Browser-Use Integration

`scraper.py` usa browser-use con modelo `bu-1-0` (cloud). El agente:
- Recibe tarea en lenguaje natural describiendo qué extraer
- Navega Google Maps autónomamente
- Usa action `extract` para obtener datos estructurados en markdown
- NO requiere langchain (se eliminó esa dependencia)

**Parsing crítico**: `_parse_results()` busca en `result.history` el `extracted_content` de las acciones del agente, no en un campo directo del resultado.

### Logging Timestamped

Cada ejecución crea `logs/scraper_YYYYMMDD_HHMMSS.log` con:
- Timestamp de cada acción
- INFO/ERROR levels
- Output simultáneo a consola y archivo
- NO usa buffering para permitir seguimiento en tiempo real

## Variables de Entorno Requeridas

```
BROWSER_USE_API_KEY=    # API key de browser-use cloud
OPENAI_API_KEY=         # Backup para modelos locales (no usado actualmente)
```

## Decisiones de Diseño Importantes

### Por qué SQLite y no PostgreSQL
- Dataset esperado: ~110K agencias (11K CPs × ~10 agencias promedio)
- SQLite maneja esto perfectamente sin overhead de servidor
- Simplicidad deployment: un solo archivo `.db`
- Índices en `postal_code` y `hash` proveen performance suficiente

### Por qué Priorización por Proximidad a 41007
- 41007 es el CP de interés primario (Sevilla)
- Al buscar CPs cercanos primero, se obtienen datos relevantes más rápido
- Si el proceso se interrumpe, ya se tiene data geográficamente útil

### Por qué Rate Limiting de 2s
- Google Maps tiene detección de bots
- Browser-use incluye técnicas anti-detección pero el rate limiting adicional reduce riesgo
- 2s es balance entre throughput y seguridad

### Por qué Markdown como Formato Intermedio
- Browser-use `extract` action retorna naturalmente markdown
- Más fácil para el LLM generar tablas markdown estructuradas
- Parseable con lógica simple línea por línea sin dependencias adicionales

## Limitaciones Conocidas

- Email raramente disponible en Google Maps (campo casi siempre vacío)
- Ratings pueden no parsearse si Google Maps cambia formato
- El agente puede fallar en páginas con CAPTCHAs agresivos
- URLs de Google Maps en resultados son placeholder, no links específicos por negocio

## Problemas Identificados Agente browser-use (Análisis 2025-11-06)

### Scroll Inefectivo
- **Síntoma**: 1582 scrolls ejecutados pero siempre 961px genérico en página principal
- **Causa**: No identifica contenedor específico de resultados de Google Maps (`div[role="feed"]` o `.m6QErb`)
- **Impacto**: Solo carga resultados iniciales, no scroll real del panel lateral
- **Fix necesario**: Modificar prompt para que agente use `evaluate()` para encontrar contenedor scrollable específico

### Errores de Validación Masivos
- **Síntoma**: 170 errores Pydantic de validación en formato de actions
- **Causa**: Agente envía `{'extract': {'query': '...'}}` cuando browser-use espera formato diferente
- **Impacto**: Múltiples reintentos (1/4, 2/4...) que alargan ejecución
- **Reintentos**: Sistema retry funciona pero ineficiente

### Logs Duplicados
- **Síntoma**: Cada mensaje de log se repite 11 veces consecutivas
- **Causa**: Probablemente múltiples handlers de logging o llamadas duplicadas
- **Impacto**: Logs de 3.1MB para tarea simple, dificulta debugging
- **Líneas afectadas**: logs/scraper_20251106_201256.log:24900-25054

### Loops Excesivos
- **Síntoma**: 782 steps totales para completar una búsqueda simple
- **Esperado**: ~15-20 steps máximo (navegar, aceptar cookies, buscar, scroll N veces, extract, done)
- **Impacto**: Tareas simples toman 9+ minutos, costo API alto
- **Causa raíz**: Combinación de scroll inefectivo + errores validación + lógica retry

### Extracción Incompleta
- **Síntoma**: Solo extrae 2-10 agencias visibles inicialmente
- **Esperado**: Todas las agencias del área (típicamente 20-50+)
- **Causa**: Scroll inefectivo no carga más resultados en el panel
- **Prompt actual**: Dice "Extrae TODAS las agencias" pero agente no puede ver más por falta de scroll funcional

### Razonamiento del Agente
**Lo hace bien**:
- Navegación inicial coherente (Maps → cookies → búsqueda)
- Memory tracking entre steps es lógico
- Eventualmente completa tarea (Step 14/782)
- Reintentos funcionan después de errores

**Lo hace mal**:
- No detecta que scroll no está funcionando
- No ajusta estrategia cuando ve siempre "961px scrolled" sin nuevos elementos
- No identifica el elemento DOM correcto para scrollear

## Datos Fuente

Códigos postales importados desde INE (Instituto Nacional de Estadística) vía:
`https://raw.githubusercontent.com/inigoflores/ds-codigos-postales-ine-es/master/data/codigos_postales_municipios.csv`

Fuente oficial gubernamental, actualizada regularmente.
