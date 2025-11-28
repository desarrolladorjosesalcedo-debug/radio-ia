#!/bin/bash
# run.sh
# Script para ejecutar la aplicación Radio IA
# Activa el entorno virtual y lanza el programa principal

set -e

echo "======================================"
echo "       🎙️  Iniciando Radio IA"
echo "======================================"

# Cambiar al directorio del proyecto
cd "$(dirname "$0")/.."

# Verificar que existe el código fuente
if [ ! -f "src/main.py" ]; then
    echo "Error: No se encuentra src/main.py"
    exit 1
fi

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "Activando entorno virtual..."
    source venv/bin/activate
fi

# Ejecutar la aplicación
echo "Iniciando Radio IA..."
echo ""
python3 src/main.py

echo ""
echo "======================================"
echo "   Radio IA finalizada"
echo "======================================"
