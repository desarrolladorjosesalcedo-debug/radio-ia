#!/bin/bash
# install_dependencies.sh
# Script para instalar todas las dependencias del proyecto Radio IA
# Incluye Piper TTS, librerías Python y otros requisitos del sistema

set -e

echo "======================================"
echo "  Radio IA - Instalación de Dependencias"
echo "======================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar comandos
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 está instalado"
        return 0
    else
        echo -e "${RED}✗${NC} $1 no está instalado"
        return 1
    fi
}

echo ""
echo "1. Verificando Python..."
if check_command python3; then
    python3 --version
else
    echo -e "${RED}Error: Python 3 no está instalado${NC}"
    echo "Instala Python desde: https://www.python.org/downloads/"
    exit 1
fi

echo ""
echo "2. Verificando pip..."
if check_command pip3; then
    pip3 --version
else
    echo -e "${YELLOW}Instalando pip...${NC}"
    python3 -m ensurepip --upgrade
fi

echo ""
echo "3. Instalando dependencias Python..."
pip3 install -r requirements.txt

echo ""
echo "4. Verificando Ollama..."
if check_command ollama; then
    ollama --version
    echo -e "${GREEN}Ollama instalado correctamente${NC}"
else
    echo -e "${YELLOW}Ollama no encontrado${NC}"
    echo "Instala Ollama desde: https://ollama.ai/"
    echo "Luego ejecuta: ollama pull llama2"
fi

echo ""
echo "5. Verificando Piper TTS..."
if check_command piper; then
    piper --version
    echo -e "${GREEN}Piper instalado correctamente${NC}"
else
    echo -e "${YELLOW}Piper no encontrado${NC}"
    echo "Instala Piper desde: https://github.com/rhasspy/piper"
fi

echo ""
echo "6. Verificando FFmpeg..."
if check_command ffplay; then
    ffplay -version | head -1
    echo -e "${GREEN}FFmpeg instalado correctamente${NC}"
else
    echo -e "${YELLOW}FFmpeg no encontrado${NC}"
    echo "Instala FFmpeg desde: https://ffmpeg.org/download.html"
fi

echo ""
echo "======================================"
echo -e "${GREEN}Instalación completada${NC}"
echo "======================================"
echo ""
echo "Próximos pasos:"
echo "1. Descarga un modelo de voz de Piper:"
echo "   https://github.com/rhasspy/piper/releases"
echo "2. Colócalo en: models/piper/"
echo "3. Actualiza config/settings.yaml con la ruta del modelo"
echo "4. Ejecuta: bash scripts/run.sh"
echo ""
