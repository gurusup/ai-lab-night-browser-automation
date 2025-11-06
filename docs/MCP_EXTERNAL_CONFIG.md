# Configuración MCP Externa

Guía para usar el servidor MCP de QA Automation desde otros proyectos o ubicaciones.

## Ubicación del Proyecto

```
/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation
```

## Opción 1: Claude Desktop (Recomendado)

### Paso 1: Editar la Configuración de Claude Desktop

Abre el archivo de configuración:
```bash
# En macOS
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# En Linux
nano ~/.config/Claude/claude_desktop_config.json

# En Windows
notepad %APPDATA%\Claude\claude_desktop_config.json
```

### Paso 2: Agregar el Servidor

**Método A: Usando UV con --directory (Recomendado)**
```json
{
  "mcpServers": {
    "qa-automation": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation",
        "python",
        "-m",
        "src.mcp_server.qa_mcp_server"
      ],
      "env": {
        "HEADLESS_MODE": "false"
      }
    }
  }
}
```

**Método B: Usando el Virtual Environment Directamente**
```json
{
  "mcpServers": {
    "qa-automation": {
      "command": "/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation/.venv/bin/python",
      "args": [
        "-m",
        "src.mcp_server.qa_mcp_server"
      ],
      "cwd": "/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation"
    }
  }
}
```

### Paso 3: Reiniciar Claude Desktop

Después de guardar la configuración, reinicia Claude Desktop.

### Paso 4: Verificar

En Claude Desktop, escribe:
```
What tools do you have available?
```

Deberías ver las herramientas de QA automation listadas.

---

## Opción 2: Cursor / VS Code con MCP Extension

### Paso 1: Instalar la Extensión MCP

- **Cursor**: Busca "MCP" en las extensiones
- **VS Code**: Instala la extensión MCP oficial

### Paso 2: Crear Configuración

Crea `.cursor/mcp.json` o `.vscode/mcp.json` en tu proyecto:

```json
{
  "mcpServers": {
    "qa-automation": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation",
        "python",
        "-m",
        "src.mcp_server.qa_mcp_server"
      ]
    }
  }
}
```

### Paso 3: Usar en el IDE

Ahora puedes usar comandos como:
```
@mcp qa-automation: Test the homepage of thehoffbrand.com
```

---

## Opción 3: Desde Otro Proyecto Python

### Paso 1: Instalar mcp-use en tu Proyecto

```bash
pip install mcp-use
```

### Paso 2: Crear Cliente

```python
# tu_proyecto/test_qa.py
import asyncio
from mcp_use import MCPClient

async def main():
    # Configuración apuntando al proyecto externo
    config = {
        "mcpServers": {
            "qa-automation": {
                "command": "uv",
                "args": [
                    "run",
                    "--directory",
                    "/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation",
                    "python",
                    "-m",
                    "src.mcp_server.qa_mcp_server"
                ]
            }
        }
    }

    client = MCPClient.from_dict(config)

    try:
        await client.create_all_sessions()
        session = client.get_session("qa-automation")

        # Llamar herramienta
        result = await session.call_tool(
            name="qa_execute_test",
            arguments={"task": "Navigate to https://thehoffbrand.com"}
        )

        print(result.content[0].text)

    finally:
        await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(main())
```

### Paso 3: Ejecutar

```bash
python tu_proyecto/test_qa.py
```

---

## Opción 4: Variables de Entorno

Si necesitas pasar API keys desde otro proyecto:

```json
{
  "mcpServers": {
    "qa-automation": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation",
        "python",
        "-m",
        "src.mcp_server.qa_mcp_server"
      ],
      "env": {
        "BROWSER_USE_API_KEY": "bu_tu_key_aqui",
        "HEADLESS_MODE": "true",
        "SCREENSHOTS_DIR": "/tmp/qa_screenshots"
      }
    }
  }
}
```

---

## Configuración Portátil

Si quieres compartir la configuración con otros, crea un archivo `mcp_setup.sh`:

```bash
#!/bin/bash
# mcp_setup.sh - Configura el servidor MCP para Claude Desktop

PROJECT_DIR="/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation"
CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Crear configuración
cat > "$CONFIG_FILE" <<EOF
{
  "mcpServers": {
    "qa-automation": {
      "command": "$PROJECT_DIR/run_mcp_server.sh",
      "description": "QA Automation with intelligent browser Agent"
    }
  }
}
EOF

echo "✅ Configuración MCP instalada en Claude Desktop"
echo "📍 Ubicación: $CONFIG_FILE"
echo "🔄 Reinicia Claude Desktop para activar"
```

Luego ejecuta:
```bash
chmod +x mcp_setup.sh
./mcp_setup.sh
```

---

## Troubleshooting

### Problema: "Command not found"

**Solución 1:** Usa rutas absolutas
```json
{
  "command": "/usr/local/bin/uv"
}
```

**Solución 2:** Agrega PATH
```json
{
  "env": {
    "PATH": "/usr/local/bin:/usr/bin:/bin"
  }
}
```

### Problema: "Python module not found"

**Solución:** Asegúrate de que el `cwd` o `--directory` apunta al proyecto:
```json
{
  "command": "uv",
  "args": [
    "run",
    "--directory",
    "/ruta/completa/al/proyecto",
    "python",
    "-m",
    "src.mcp_server.qa_mcp_server"
  ]
}
```

### Problema: "API key not found"

**Solución 1:** Pasa las variables de entorno
```json
{
  "env": {
    "BROWSER_USE_API_KEY": "tu_key_aqui"
  }
}
```

**Solución 2:** Asegúrate de que el `.env` existe en el proyecto
```bash
cd /ruta/al/proyecto
cp .env.example .env
# Edita .env con tus keys
```

---

## Verificación

Para verificar que todo funciona:

### Test 1: Verificar que el servidor inicia
```bash
# Ejecuta el servidor directamente
cd /Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation
uv run python -m src.mcp_server.qa_mcp_server
```

Deberías ver logs del servidor MCP esperando conexiones (stdin/stdout).

### Test 2: Verificar desde Claude Desktop

En Claude Desktop:
```
List all available tools and tell me what each one does
```

### Test 3: Ejecutar un test simple

En Claude Desktop:
```
Search for SEVEN RUNNER METALLIC COPPER on https://thehoffbrand.com/,
add it to cart and generate screenshot
```

---

## Rutas Importantes

Guarda estas rutas para referencia rápida:

```bash
# Proyecto
/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation

# Script wrapper
/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation/run_mcp_server.sh

# Virtual env Python
/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation/.venv/bin/python

# Screenshots (por defecto)
/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation/screenshots/

# Configuración Claude Desktop (macOS)
~/Library/Application Support/Claude/claude_desktop_config.json
```

---

## Ejemplo Completo: Claude Desktop en macOS

```json
{
  "mcpServers": {
    "qa-automation": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/oliver/Sites/community/gurusup/ai-lab-night-browser-automation",
        "python",
        "-m",
        "src.mcp_server.qa_mcp_server"
      ],
      "description": "QA Automation with intelligent browser automation",
      "env": {
        "HEADLESS_MODE": "false",
        "SCREENSHOTS_DIR": "/Users/oliver/Desktop/qa-screenshots"
      }
    }
  }
}
```

Después de guardar, reinicia Claude y prueba:
```
Search for SEVEN RUNNER METALLIC COPPER on https://thehoffbrand.com/,
add it to cart and generate screenshot
```

---

**Última actualización:** 2025-11-06
