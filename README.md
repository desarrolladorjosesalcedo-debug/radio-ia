# 🎙️ Radio IA

**Radio automatizada generada por inteligencia artificial 100% local**

Radio IA es una aplicación que genera y transmite contenido de radio de forma continua utilizando modelos de IA locales. Sin APIs externas, sin costos recurrentes, sin límites.

## ✨ Características

- 🤖 **Contenido generado por IA**: Usa Ollama (llama2, mistral, etc.) para crear locuciones naturales
- 🎤 **Voz sintetizada**: Piper TTS convierte texto a voz de alta calidad
- 📻 **Transmisión continua**: Genera y reproduce contenido sin parar
- 🎨 **Múltiples temas**: Programación, tecnología, chistes, reflexiones, y más
- ⚙️ **Altamente configurable**: Personaliza duración, tono, estilo y temas
- 💻 **100% Local**: Todo corre en tu máquina, sin internet

## 🏗️ Arquitectura

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   topics    │────▶│  prompt  │────▶│  Ollama  │────▶│  Piper   │
│ (aleatorio) │     │(construye)│    │  (texto) │     │  (voz)   │
└─────────────┘     └──────────┘     └──────────┘     └──────────┘
                                                              │
                                                              ▼
                                     ┌──────────────────────────┐
                                     │     ffplay (audio)       │
                                     │   🔊 Reproducción en     │
                                     │      tiempo real         │
                                     └──────────────────────────┘
```

## 📋 Requisitos

### Software necesario:

1. **Python 3.8+** - [Descargar](https://www.python.org/downloads/)
2. **Ollama** - [Descargar](https://ollama.ai/)
3. **Piper TTS** - [Descargar](https://github.com/rhasspy/piper/releases)
4. **FFmpeg** - [Descargar](https://ffmpeg.org/download.html)

### Modelo de voz:
- **IMPORTANTE**: Los modelos de Piper NO están incluidos en el repositorio por su tamaño
- Descarga el modelo de voz español desde: [Piper Releases](https://github.com/rhasspy/piper/releases)
- Recomendado: `es_ES-davefx-medium.onnx` (~63 MB)
- Coloca los archivos `.onnx` y `.onnx.json` en `models/piper/`

## 🚀 Instalación

### Opción 1: Instalación automática (Linux/Mac)

```bash
# Clonar el repositorio
git clone https://github.com/desarrolladorjosesalcedo-debug/radio-ia.git
cd radio-ia

# Instalar dependencias
bash scripts/install_dependencies.sh

# Descargar modelo de Ollama
ollama pull llama2

# Descargar modelo de Piper y colocarlo en models/piper/
# Desde: https://github.com/rhasspy/piper/releases/latest
# Archivos: es_ES-davefx-medium.onnx y es_ES-davefx-medium.onnx.json
```

### Opción 2: Instalación manual (Windows)

```powershell
# 0. Clonar el repositorio
git clone https://github.com/desarrolladorjosesalcedo-debug/radio-ia.git
cd radio-ia

# 1. Crear y activar entorno virtual
.\scripts\setup_venv.ps1

# 2. Instalar herramientas externas
.\scripts\install_dependencies.ps1

# 3. Descargar modelo de Ollama (si usas Ollama)
ollama pull llama2

# 4. Descargar modelo de Piper (OBLIGATORIO)
# Desde: https://github.com/rhasspy/piper/releases/latest
# Archivos necesarios:
#   - es_ES-davefx-medium.onnx (~63 MB)
#   - es_ES-davefx-medium.onnx.json (~4 KB)
# Colocar en: models/piper/

# 5. Configurar Groq API (opcional pero recomendado)
# Editar config/settings.yaml con tu API key de Groq
# Obtener API key gratis en: https://console.groq.com/
```

**Nota**: Los scripts de PowerShell requieren permisos de ejecución. Si hay error, ejecuta:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## ⚙️ Configuración

Edita `config/settings.yaml` para personalizar:

```yaml
llm:
  model_name: "llama2"  # Tu modelo de Ollama

tts:
  model_path: "models/piper/es_ES-davefx-medium.onnx"  # Tu modelo de voz

radio:
  duration_seconds: 20  # Duración de cada segmento
  delay_seconds: 1.0    # Pausa entre segmentos

personality:
  preset: "standard"     # standard, morning_show, night_talk, comedy
  energy_level: "medio"  # alto, medio, bajo, relajado
  style: "informativo"   # informativo, entretenido, reflexivo, humorístico
```

## 🎯 Uso

### Linux/Mac:
```bash
bash scripts/run.sh
```

### Windows:
```powershell
python src/main.py
```

### Detener la radio:
Presiona `Ctrl+C` para detener la transmisión de forma elegante.

## 📁 Estructura del Proyecto

```
radio-ia/
├── src/
│   ├── main.py                  # Punto de entrada
│   ├── core/
│   │   ├── radio_loop.py       # Motor principal (orquestador)
│   │   ├── topics.py           # Gestión de temas
│   │   └── prompt.py           # Generación de prompts
│   ├── llm/
│   │   └── ollama_client.py    # Cliente de Ollama
│   ├── tts/
│   │   ├── piper_tts.py        # Cliente de Piper TTS
│   │   └── config.json         # Configuración de voz
│   └── utils/
│       └── audio_player.py     # Reproductor de audio
├── models/piper/               # Modelos de voz
├── config/
│   ├── settings.yaml           # Configuración principal
│   └── env.example             # Variables de entorno
├── scripts/
│   ├── install_dependencies.sh # Instalador (Linux/Mac)
│   └── run.sh                  # Ejecutor (Linux/Mac)
└── requirements.txt            # Dependencias Python
```

## 🎨 Personalización

### Agregar temas personalizados:

Edita `config/settings.yaml`:

```yaml
custom_topics:
  - "historia del rock"
  - "recetas de cocina"
  - "filosofía antigua"
```

### Cambiar la personalidad:

```yaml
personality:
  preset: "morning_show"  # Energética y animada
  energy_level: "alto"
  style: "entretenido"
```

### Ajustar velocidad de voz:

```yaml
tts:
  length_scale: 0.9  # Más rápido
  # length_scale: 1.2  # Más lento
```

## 🔧 Troubleshooting

### "Ollama no está instalado"
- Verifica que Ollama esté en el PATH
- Ejecuta: `ollama --version`

### "Piper no está instalado"
- Descarga Piper desde [GitHub releases](https://github.com/rhasspy/piper/releases)
- Agrega el ejecutable al PATH del sistema

### "Modelo de Piper no encontrado"
- Descarga un modelo desde [Piper releases](https://github.com/rhasspy/piper/releases)
- Colócalo en `models/piper/`
- Actualiza la ruta en `config/settings.yaml`

### "ffplay no está disponible"
- Instala FFmpeg desde [ffmpeg.org](https://ffmpeg.org/)
- En Windows, agrega FFmpeg al PATH

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 TODO

- [ ] Soporte para múltiples idiomas
- [ ] Efectos de sonido entre segmentos
- [ ] Música de fondo
- [ ] Web UI para control remoto
- [ ] Streaming a servidor de radio

## 📄 Licencia

MIT License - siéntete libre de usar este proyecto como quieras.

## 🙏 Créditos

- [Ollama](https://ollama.ai/) - Modelos de lenguaje locales
- [Piper TTS](https://github.com/rhasspy/piper) - Síntesis de voz
- [FFmpeg](https://ffmpeg.org/) - Procesamiento de audio

---

Hecho con ❤️ y mucha IA
