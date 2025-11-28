# Descarga de Modelos de Piper TTS

Los modelos de voz de Piper NO están incluidos en el repositorio debido a su tamaño (~63 MB).

## 📥 Descargar modelo de voz español

### Opción 1: Descarga manual

1. Visita: https://github.com/rhasspy/piper/releases/latest
2. Busca los archivos del modelo español:
   - `es_ES-davefx-medium.onnx` (~63 MB)
   - `es_ES-davefx-medium.onnx.json` (~4 KB)
3. Descarga ambos archivos
4. Copia ambos archivos a la carpeta `models/piper/`

### Opción 2: Descarga con script (PowerShell)

```powershell
# Descargar modelo español
$url_onnx = "https://github.com/rhasspy/piper/releases/download/v1.2.0/es_ES-davefx-medium.onnx"
$url_json = "https://github.com/rhasspy/piper/releases/download/v1.2.0/es_ES-davefx-medium.onnx.json"

# Crear directorio si no existe
New-Item -ItemType Directory -Force -Path "models/piper"

# Descargar archivos
Invoke-WebRequest -Uri $url_onnx -OutFile "models/piper/es_ES-davefx-medium.onnx"
Invoke-WebRequest -Uri $url_json -OutFile "models/piper/es_ES-davefx-medium.onnx.json"

Write-Host "✅ Modelo descargado exitosamente"
```

### Opción 3: Descarga con curl (Linux/Mac)

```bash
# Crear directorio
mkdir -p models/piper

# Descargar modelo
curl -L "https://github.com/rhasspy/piper/releases/download/v1.2.0/es_ES-davefx-medium.onnx" \
  -o "models/piper/es_ES-davefx-medium.onnx"

curl -L "https://github.com/rhasspy/piper/releases/download/v1.2.0/es_ES-davefx-medium.onnx.json" \
  -o "models/piper/es_ES-davefx-medium.onnx.json"

echo "✅ Modelo descargado exitosamente"
```

## 🗂️ Estructura esperada

Después de la descarga, tu carpeta `models/piper/` debe contener:

```
models/piper/
├── es_ES-davefx-medium.onnx         (~63 MB)
└── es_ES-davefx-medium.onnx.json    (~4 KB)
```

## 🌍 Otros idiomas disponibles

Si deseas usar otro idioma, visita:
https://github.com/rhasspy/piper/blob/master/VOICES.md

Descarga el modelo correspondiente y actualiza la ruta en `config/settings.yaml`:

```yaml
tts:
  model_path: "models/piper/tu-modelo.onnx"
```

## ⚠️ Notas importantes

- Los modelos de Piper están en `.gitignore` por su tamaño
- Cada colaborador debe descargar los modelos localmente
- Los modelos son necesarios para que la aplicación funcione
- Sin los modelos, obtendrás un error al iniciar la radio
