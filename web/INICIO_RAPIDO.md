# 🎯 GUÍA RÁPIDA - Iniciar Interfaz Web

## ✅ Todo está listo. Sigue estos pasos:

### 1️⃣ Iniciar el servidor

```powershell
cd web
python api_server.py
```

**Verás:**
```
============================================================
🎙️  RADIO IA - SERVIDOR WEB
============================================================

📡 Servidor iniciando en http://localhost:8000
🌐 Abre tu navegador en: http://localhost:8000

Presiona Ctrl+C para detener el servidor
============================================================
```

### 2️⃣ Abrir el navegador

Ve a: **http://localhost:8000**

### 3️⃣ Controlar la radio

#### Controles disponibles:
- **🟢 Iniciar**: Inicia la radio
- **🟡 Pausar**: Pausa la transmisión (¡ahora funciona!)
- **🔵 Reanudar**: Continúa desde donde pausó (¡ahora funciona!)
- **🔴 Detener**: Detiene completamente

#### Modos:
- **TOPICS**: Temas aleatorios variados
- **MONOLOGUE**: Monólogo continuo sobre un tema específico

### 4️⃣ Probar pause/resume

1. Haz clic en **Iniciar**
2. Espera que empiece a reproducir
3. Haz clic en **Pausar** → La radio se pausa al terminar el segmento actual
4. Haz clic en **Reanudar** → La radio continúa desde donde pausó
5. Haz clic en **Detener** → La radio se detiene completamente

## 🎨 Nuevas funcionalidades implementadas

✅ **Pause real**: Ya no es simulado, la radio realmente se pausa
✅ **Resume funcional**: Continúa exactamente donde pausó
✅ **Stop mejorado**: Detención limpia con cleanup de threads
✅ **Control desde navegador**: Manejo completo desde la interfaz web

## 🔧 Cambios técnicos realizados

### En `radio_loop.py`:
- ✅ Agregadas flags globales `_stop_flag` y `_pause_flag`
- ✅ Modificada función `start_radio()` para aceptar flags
- ✅ Implementado check de pausa en el loop principal
- ✅ Check de detención antes de generar siguiente segmento
- ✅ Manejo de pausa durante generación en background

### En `api_server.py`:
- ✅ Actualizado `radio_worker()` para pasar flags
- ✅ Mejorado endpoint `/pause` con control real
- ✅ Mejorado endpoint `/resume` con control real
- ✅ Mejorado endpoint `/stop` con desbloqueo de pausa

## 🐛 Comportamiento esperado

### Al pausar:
```
⏸️  Radio en pausa...
```
- Se muestra cada 0.5 segundos mientras está pausada
- No genera nuevos segmentos
- No consume recursos de IA

### Al reanudar:
```
▶️  Radio reanudada
```
- Continúa inmediatamente
- Genera el siguiente segmento
- Todo vuelve a la normalidad

### Al detener:
```
🛑 Señal de detención recibida
💾 Sesión guardada: 20251212_143000
```
- Detención limpia
- Sesión guardada automáticamente
- Thread termina correctamente

## 📱 Desde el navegador

El estado se actualiza en tiempo real cada 2 segundos:
- Badge cambia de color según estado
- Botones se habilitan/deshabilitan según corresponda
- Notificaciones toast confirman cada acción

## ⚠️ Notas importantes

1. **Pausa inteligente**: La radio completa el segmento actual antes de pausar (no corta a mitad de palabra)

2. **Generación en background**: Si hay un segmento generándose en paralelo, la pausa espera a que termine

3. **Compatibilidad**: La radio sigue funcionando igual desde terminal (`python src/main.py`) sin los flags

4. **Thread safety**: Los flags son thread-safe (threading.Event) y seguros para uso concurrente

## 🎉 ¡Listo para probar!

Ejecuta:
```powershell
cd web
python api_server.py
```

Y abre **http://localhost:8000** en tu navegador.

---

**¿Problemas?** Revisa:
- Que el servidor esté corriendo
- Que no haya errores en la consola
- Que las dependencias estén instaladas (`fastapi`, `uvicorn`)
