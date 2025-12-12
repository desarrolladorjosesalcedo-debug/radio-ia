# 🌐 Interfaz Web para Radio IA

Panel de control web para manejar tu Radio IA desde el navegador.

## 📋 Características

- ✅ **Control completo**: Iniciar, pausar, reanudar y detener la radio
- ✅ **Selección de modo**: Cambiar entre TOPICS y MONOLOGUE
- ✅ **Temas personalizados**: Ingresar tema para monólogos
- ✅ **Historial de sesiones**: Ver y reproducir sesiones anteriores
- ✅ **Estado en tiempo real**: Monitoreo del estado de la radio
- ✅ **Diseño responsive**: Compatible con móviles y tablets
- ✅ **Notificaciones**: Toast messages para feedback visual

## 🚀 Instalación

### 1. Instalar dependencias del servidor web

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar FastAPI y uvicorn
pip install fastapi uvicorn[standard] python-multipart
```

O actualizar desde requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Verificar estructura de archivos

```
radio-ia/
├── web/
│   ├── api_server.py       # Servidor FastAPI
│   ├── index.html          # Interfaz web
│   └── static/
│       └── app.js          # JavaScript frontend
├── src/                    # Tu código existente
├── config/
│   └── settings.yaml
└── requirements.txt
```

## 🎯 Uso

### Iniciar el servidor web

```bash
# Desde la carpeta raíz del proyecto
cd web
python api_server.py
```

Verás:

```
🎙️  RADIO IA - SERVIDOR WEB
============================================================

📡 Servidor iniciando en http://localhost:8000
🌐 Abre tu navegador en: http://localhost:8000

Presiona Ctrl+C para detener el servidor
============================================================
```

### Abrir la interfaz

1. Abre tu navegador
2. Ve a: **http://localhost:8000**
3. ¡Listo! Ya puedes controlar tu radio

## 🎛️ Funcionalidades

### Botones de Control

- **🟢 Iniciar**: Inicia la radio en el modo seleccionado
- **🟡 Pausar**: Pausa la transmisión actual
- **🔵 Reanudar**: Continúa desde donde se pausó
- **🔴 Detener**: Detiene completamente la radio

### Modos de Operación

1. **TOPICS** (Temas aleatorios)
   - Genera contenido sobre temas variados
   - Usa la lista de tópicos predefinida
   
2. **MONOLOGUE** (Monólogo continuo)
   - Genera un monólogo sobre un tema específico
   - Requiere ingresar un tema en el campo de texto

### Sesiones Guardadas

- Ver todas las sesiones anteriores
- Información: fecha, duración, número de segmentos
- Botón para reproducir cualquier sesión
- Actualización manual con botón "Actualizar"

### Estado en Tiempo Real

El panel muestra el estado actual:
- **DETENIDO** (gris): Radio apagada
- **ENCENDIDA** (verde pulsante): Transmitiendo
- **PAUSADA** (amarillo): En pausa
- **GENERANDO** (azul pulsante): Creando contenido
- **REPRODUCIENDO** (morado pulsante): Reproduciendo audio

## 📡 API Endpoints

El servidor expone los siguientes endpoints REST:

### Control de Radio

```http
POST /api/start
Content-Type: application/json

{
  "mode": "topics",  // o "monologue"
  "theme": "inteligencia artificial",  // opcional, solo para monologue
  "skip_intro": false
}
```

```http
POST /api/pause
POST /api/resume
POST /api/stop
```

### Configuración

```http
POST /api/set_mode
Content-Type: application/json

{
  "mode": "monologue"
}
```

### Estado

```http
GET /api/status

Response:
{
  "status": "running",
  "mode": "topics",
  "is_running": true,
  "is_paused": false,
  "theme": null
}
```

### Sesiones

```http
GET /api/list_sessions

Response:
{
  "success": true,
  "sessions": [
    {
      "id": "20251212_143000",
      "date": "2025-12-12 14:30",
      "segments": 5,
      "duration": "150s aprox."
    }
  ],
  "total": 1
}
```

```http
POST /api/play_session/{session_id}
```

## 🔧 Configuración Avanzada

### Cambiar puerto del servidor

Edita `api_server.py`:

```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8080,  # Cambiar aquí
    log_level="info"
)
```

### Configurar CORS

Para acceso desde otros dominios, edita `api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://mi-dominio.com"],  # Especifica dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐛 Troubleshooting

### Error: "No se pudo conectar al servidor"

**Solución**: Asegúrate de que el servidor esté ejecutándose:
```bash
cd web
python api_server.py
```

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solución**: Instala las dependencias:
```bash
pip install fastapi uvicorn[standard]
```

### Las sesiones no aparecen

**Solución**: Verifica que existan sesiones en la carpeta `history/`:
```bash
ls history/
```

### La radio no se detiene correctamente

**Limitación conocida**: La implementación actual de `radio_loop.py` corre en loop infinito. Para detener completamente, reinicia el servidor.

**Workaround**: Usa Ctrl+C en la terminal del servidor.

## 🌐 Desplegar en Render.com (Opcional)

Para hacer tu radio accesible desde internet:

### 1. Crear archivo de configuración

Crea `render.yaml` en la raíz:

```yaml
services:
  - type: web
    name: radio-ia-web
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "cd web && python api_server.py"
    envVars:
      - key: PYTHON_VERSION
        value: 3.9
```

### 2. Subir a GitHub

```bash
git add .
git commit -m "Agregar interfaz web"
git push
```

### 3. Conectar con Render

1. Ve a [render.com](https://render.com)
2. Crea nuevo "Web Service"
3. Conecta tu repositorio GitHub
4. Render detectará automáticamente la configuración
5. ¡Despliega!

**Nota**: En Render, la reproducción de audio será limitada. Considera generar y descargar archivos MP3 en lugar de reproducir en el servidor.

## 📱 Uso desde Móvil

La interfaz es completamente responsive. Puedes controlar tu radio desde:

1. **Red local**: Usa la IP de tu PC
   ```
   http://192.168.1.X:8000
   ```

2. **Internet** (con Render.com):
   ```
   https://tu-radio-ia.onrender.com
   ```

## 🎨 Personalización

### Cambiar colores

Edita `index.html` y modifica las clases de Tailwind:

```html
<!-- Cambiar color del botón de inicio -->
<button class="bg-green-600 hover:bg-green-700">
  <!-- Cambia a azul: -->
  <button class="bg-blue-600 hover:bg-blue-700">
```

### Agregar más funcionalidades

Añade nuevos endpoints en `api_server.py`:

```python
@app.post("/api/mi_nueva_funcion")
async def mi_funcion():
    return {"success": True}
```

Y llama desde `app.js`:

```javascript
async function miFuncion() {
    const data = await apiFetch('/mi_nueva_funcion', { method: 'POST' });
    showToast(data.message, 'success');
}
```

## 📚 Stack Tecnológico

- **Backend**: FastAPI + Uvicorn
- **Frontend**: HTML5 + TailwindCSS + Vanilla JavaScript
- **API**: RESTful JSON
- **Comunicación**: Fetch API + Polling

## 💡 Próximas Mejoras

- [ ] WebSocket para estado en tiempo real (en lugar de polling)
- [ ] Visualización de forma de onda del audio
- [ ] Editor de tópicos desde la interfaz
- [ ] Historial de reproducción con timestamps
- [ ] Download de sesiones como podcast
- [ ] Autenticación y múltiples usuarios

## 📄 Licencia

Parte del proyecto Radio IA.

---

**¿Preguntas?** Abre un issue en GitHub o consulta la documentación principal.
