# 🎙️ Radio IA

**Radio automatizada generada por inteligencia artificial**

Radio IA es una aplicación que genera y transmite contenido de radio de forma continua utilizando modelos de IA. Genera texto con LLM y sintetiza voz con calidad profesional.

## ✨ Características

- 🤖 **Contenido generado por IA**: Groq API (ultra-rápido) o Ollama (local)
- 🎙️ **Voz neuronal natural**: Microsoft Edge TTS con voces profesionales en español
- 📻 **Transmisión continua**: Genera y reproduce contenido sin parar
- 📝 **Historial de sesiones**: Guarda todo automáticamente en JSON con timestamps
- 🔁 **Replay sin pausas**: Reproduce sesiones completas sin tiempos de generación
- 🎨 **Múltiples temas**: Programación, tecnología, chistes, reflexiones, y más
- ⚙️ **Altamente configurable**: Personaliza duración, tono, estilo y temas
- 🌎 **8 voces en español**: México, Colombia, España, Argentina
- ⚡ **Ultra-rápido**: 1-2 seg generación texto, 2-3 seg síntesis voz
- 🆓 **Gratis e ilimitado**: Edge TTS 100% gratuito

## 🏗️ Arquitectura

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   topics    │────▶│  prompt  │────▶│   Groq   │────▶│Edge TTS  │
│ (aleatorio) │     │(construye)│    │  (texto) │     │  (voz)   │
└─────────────┘     └──────────┘     └──────────┘     └──────────┘
                                            1-2s              2-3s
                                                              │
                                                              ▼
                                     ┌──────────────────────────┐
                                     │     ffplay (audio)       │
                                     │   🔊 Reproducción en     │
                                     │      tiempo real         │
                                     └──────────────────────────┘
```

### Sistema de fallback TTS:
1. **Piper TTS** (local, opcional)
2. **Edge TTS** ⭐ (voces neuronales, recomendado)
3. **Google TTS** (fallback final)

## 📋 Requisitos

### Software necesario:

1. **Python 3.9+** - [Descargar](https://www.python.org/downloads/)
2. **FFmpeg** - [Descargar](https://ffmpeg.org/download.html)
3. **Groq API Key** - [Obtener gratis](https://console.groq.com/) (recomendado)
4. **Ollama** (opcional) - [Descargar](https://ollama.ai/) - Para modo 100% local

### Voces disponibles (Edge TTS):
- 🇨🇴 **Colombia**: SalomeNeural (mujer), GonzaloNeural (hombre)
- 🇲🇽 **México**: DaliaNeural (mujer), JorgeNeural (hombre)
- 🇪🇸 **España**: ElviraNeural (mujer), AlvaroNeural (hombre)
- 🇦🇷 **Argentina**: ElenaNeural (mujer), TomasNeural (hombre)

## 🚀 Instalación

### Instalación rápida (Windows)

```powershell
# 1. Clonar el repositorio
git clone https://github.com/desarrolladorjosesalcedo-debug/radio-ia.git
cd radio-ia

# 2. Crear y activar entorno virtual
.\scripts\setup_venv.ps1

# 3. Instalar FFmpeg (si no lo tienes)
winget install -e --id Gyan.FFmpeg

# 4. Configurar Groq API
# Edita config/settings.yaml y agrega tu API key de Groq
# Obtén una gratis en: https://console.groq.com/

# 5. Activar entorno (IMPORTANTE: ejecutar en cada sesión nueva)
.\activate.ps1

# 6. Ejecutar la radio
python src/main.py
# o usar el script:
.\scripts\run.ps1
```

**💡 Nota importante para Windows:** Si `python src/main.py` no funciona, usa `.\activate.ps1` primero. Este script configura el PATH correctamente para que FFmpeg y Python funcionen.

### Instalación alternativa (Linux/Mac)

```bash
# 1. Clonar el repositorio
git clone https://github.com/desarrolladorjosesalcedo-debug/radio-ia.git
cd radio-ia

# 2. Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Instalar FFmpeg
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg

# 4. Configurar Groq API en config/settings.yaml

# 5. Ejecutar
python src/main.py
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
  provider: "groq"  # "groq" (rápido) o "ollama" (local)
  model_name: "llama-3.3-70b-versatile"
  api_key: "tu-api-key-aqui"  # De https://console.groq.com/

tts:
  edge_voice: "es-CO-SalomeNeural"  # Voz de Colombia (mujer)
  # Otras opciones:
  #   es-CO-GonzaloNeural (Colombia, hombre)
  #   es-MX-DaliaNeural (México, mujer)
  #   es-ES-ElviraNeural (España, mujer)

radio:
  duration_seconds: 15  # Duración de cada segmento
  delay_seconds: 2.0    # Pausa entre segmentos

personality:
  preset: "standard"     # standard, morning_show, night_talk, comedy
  energy_level: "medio"  # alto, medio, bajo, relajado
  style: "informativo"   # informativo, entretenido, reflexivo
```

## 🎯 Uso

### Iniciar radio en vivo
```powershell
# Windows
.\scripts\run.ps1
# o directamente:
python src/main.py

# Sin introducción
python src/main.py --skip-intro

# Con pausa personalizada (3 segundos entre segmentos)
python src/main.py --delay 3.0
```

### Gestión de historial de sesiones

Cada vez que escuchas la radio, se guarda automáticamente en `history/`:

```powershell
# Ver todas las sesiones guardadas
python src/main.py --list-sessions

# Ver texto completo de una sesión
python src/main.py --show 20251128_143000

# Reproducir una sesión sin pausas (solo 2s entre segmentos)
python src/main.py --replay 20251128_143000

# Reproducir con delay personalizado
python src/main.py --replay 20251128_143000 --delay 1.0
```

**Ventajas del replay:**
- ✅ Sin pausas de generación (audio instantáneo)
- ✅ Texto guardado para referencia
- ✅ Puedes volver a escuchar tus sesiones favoritas
- ✅ Perfecto para compartir contenido específico

### Detener la radio:
Presiona `Ctrl+C` para detener la transmisión de forma elegante. La sesión se guardará automáticamente.

## 📁 Estructura del Proyecto

```
radio-ia/
├── src/
│   ├── main.py                  # Punto de entrada
│   ├── core/
│   │   ├── radio_loop.py       # Orquestador principal con fallback TTS
│   │   ├── topics.py           # 15 categorías de temas
│   │   └── prompt.py           # Generación dinámica de prompts
│   ├── llm/
│   │   ├── groq_client.py      # Cliente de Groq API (primario)
│   │   └── ollama_client.py    # Cliente de Ollama (respaldo)
│   ├── tts/
│   │   ├── edge_tts_client.py  # Microsoft Edge TTS (primario)
│   │   ├── gtts_client.py      # Google TTS (respaldo)
│   │   └── piper_tts.py        # Piper TTS (respaldo)
│   └── utils/
│       └── audio_player.py     # Reproductor FFplay
├── config/
│   └── settings.yaml           # Configuración principal
├── scripts/
│   ├── install_dependencies.ps1 # Instalador (Windows)
│   └── run.ps1                 # Ejecutor (Windows)
└── requirements.txt            # Dependencias Python
```

## 🎨 Personalización

### Cambiar voz colombiana:

```yaml
tts:
  edge_voice: "es-CO-GonzaloNeural"  # Voz masculina de Colombia
```

### Cambiar personalidad:

```yaml
personality:
  preset: "comedy"      # Divertida y espontánea
  energy_level: "alto"
  style: "humorístico"
```

### Ajustar parámetros de voz:

```yaml
tts:
  rate: "+10%"     # Velocidad (de -50% a +100%)
  volume: "+0%"    # Volumen (de -100% a +100%)
  pitch: "+5Hz"    # Tono (en Hz)
```

## 🔧 Troubleshooting

### "Error de conexión con Groq"
- Verifica tu API key en `settings.yaml`
- Confirma tu conexión a internet
- Revisa límites de uso en https://console.groq.com/

### "Audio no se reproduce"
- Verifica que FFmpeg esté instalado: `ffplay -version`
- En Windows, asegúrate de tener altavoces/audífonos conectados
- Revisa el volumen del sistema

### "TTS no genera audio"
- El sistema probará automáticamente: Edge TTS → Google TTS → Piper
- Si Edge falla, verifica conexión a internet
- Si todos fallan, revisa logs en la consola

## 🤝 Contribuir

Contribuciones bienvenidas:

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/NuevaFuncion`)
3. Commit cambios (`git commit -m 'Añadir nueva función'`)
4. Push (`git push origin feature/NuevaFuncion`)
5. Abre Pull Request

## 📝 TODO

- [x] Sistema de historial de sesiones
- [x] Replay de sesiones sin pausas
- [ ] Más voces latinoamericanas (Chile, Perú, Venezuela)
- [ ] Efectos de sonido entre segmentos
- [ ] Música de fondo con crossfade
- [ ] Web UI para control en tiempo real
- [ ] Streaming a servidor Icecast/Shoutcast
- [ ] Exportar sesiones a MP3/podcast

## 📄 Licencia

MIT License - úsalo libremente.

## 🙏 Créditos

- [Groq](https://groq.com/) - LLM ultra-rápido
- [Microsoft Edge TTS](https://github.com/rn0x/edge-tts) - Voces neurales gratuitas
- [FFmpeg](https://ffmpeg.org/) - Procesamiento de audio
- [Ollama](https://ollama.ai/) - Opción local alternativa

---

Hecho con ❤️ por José Salcedo usando IA
