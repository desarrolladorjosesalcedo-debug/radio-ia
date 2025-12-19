# 🚀 Deployment en Render.com

Esta rama (`render-deployment`) está optimizada para deployment en Render.com.

## ✅ Cambios para Cloud

1. **Streaming habilitado por defecto** - No requiere ffplay local
2. **Edge TTS como fallback** - Funciona sin Piper TTS instalado
3. **API Key desde variable de entorno** - Más seguro que archivo de configuración
4. **Detección automática de entorno cloud** - Salta validaciones de dependencias locales

## 📋 Pasos para Deploy

### 1. Preparar Repositorio

```bash
# Asegúrate de estar en la rama correcta
git checkout render-deployment
git push origin render-deployment
```

### 2. Crear Servicio en Render

1. Ve a [Render Dashboard](https://dashboard.render.com/)
2. Click en **"New +"** → **"Web Service"**
3. Conecta tu repositorio de GitHub
4. Selecciona la rama **`render-deployment`**

### 3. Configuración del Servicio

**Settings básicos:**
- **Name:** `radio-ia` (o el que prefieras)
- **Region:** Oregon (o el más cercano)
- **Branch:** `render-deployment`
- **Root Directory:** dejar vacío
- **Runtime:** Python 3.11
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `cd web && uvicorn api_server:app --host 0.0.0.0 --port $PORT`

### 4. Variables de Entorno

En la sección **Environment**, añade:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | `tu-api-key-de-groq` |
| `PYTHON_VERSION` | `3.11.0` |
| `PYTHONUNBUFFERED` | `1` |
| `RENDER` | `true` |

**⚠️ IMPORTANTE:** Obtén tu API key de Groq en [console.groq.com](https://console.groq.com/)

### 5. Desplegar

1. Click en **"Create Web Service"**
2. Render automáticamente:
   - Instalará dependencias
   - Iniciará el servidor
   - Asignará una URL pública

### 6. Acceder a la Radio

Una vez desplegado, accede a: `https://tu-servicio.onrender.com`

## 🎵 Cómo Funciona

- **TTS:** Usa Edge TTS (Microsoft) - no requiere Piper
- **Audio:** Streaming vía websockets/HTTP (no usa ffplay)
- **LLM:** Groq API (configurado vía variable de entorno)
- **Reproducción:** El audio se convierte a MP3 y se transmite al navegador

## 🔧 Diferencias con Versión Local

| Característica | Local (master) | Cloud (render-deployment) |
|----------------|----------------|---------------------------|
| Streaming | Opcional | Activado por defecto |
| TTS | Piper → Edge → Google | Edge → Google |
| Audio Player | ffplay | Navegador web |
| API Key | settings.yaml | Variable de entorno |
| Modelo Piper | Requerido | Opcional |

## 🐛 Troubleshooting

### Error: "Falta API key de Groq"
- Verifica que hayas configurado `GROQ_API_KEY` en Environment Variables

### La radio no inicia
- Revisa los logs en Render Dashboard
- Verifica que Edge TTS esté funcionando (debería estar OK por defecto)

### Audio no se escucha
- El streaming debe estar habilitado (`enable_streaming: true` en app.js)
- Verifica que el navegador permita audio
- Revisa la consola del navegador (F12)

## 📝 Notas

- **Plan Free de Render:** El servicio se "duerme" después de 15 minutos de inactividad. Primera carga puede tardar ~30 segundos.
- **Límites:** Groq API tiene rate limits en plan gratuito
- **Persistencia:** Las sesiones guardadas se perderán al reiniciar (usar volumen persistente si es necesario)

## 🔄 Actualizar Deployment

```bash
# Hacer cambios en la rama
git add .
git commit -m "Actualización"
git push origin render-deployment

# Render auto-desplegará los cambios
```
