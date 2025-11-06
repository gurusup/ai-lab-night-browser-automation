#!/bin/bash
# DevJobScout - Script de inicio rápido

echo "🚀 DevJobScout - Tu reclutador personal silencioso"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio devjobscout/"
    exit 1
fi

# Verificar que .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Advertencia: No se encontró archivo .env"
    echo "   Copia .env.example a .env y configura tus variables"
    echo ""
    read -p "¿Continuar de todas formas? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar que uv está instalado
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv no está instalado"
    echo "   Instala uv desde: https://github.com/astral-sh/uv"
    exit 1
fi

# Sincronizar dependencias
echo "📦 Sincronizando dependencias..."
uv sync

if [ $? -ne 0 ]; then
    echo "❌ Error al instalar dependencias"
    exit 1
fi

echo ""
echo "✅ Todo listo!"
echo ""
echo "🌐 Iniciando interfaz web en http://localhost:8501"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

# Iniciar Streamlit
uv run streamlit run app.py
