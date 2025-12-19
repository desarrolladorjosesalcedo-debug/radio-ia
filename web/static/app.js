// app.js - Frontend JavaScript para Radio IA
// Maneja la lógica de la interfaz y comunicación con el backend

// Configuración - Detectar automáticamente el host (local o Render)
const API_BASE_URL = window.location.origin + '/api';
let pollingInterval = null;

// Estado de la aplicación
const state = {
    currentMode: 'topics',
    isRunning: false,
    isPaused: false,
    status: 'stopped'
};

// Elementos DOM
const elements = {
    btnStart: document.getElementById('btn-start'),
    btnPause: document.getElementById('btn-pause'),
    btnResume: document.getElementById('btn-resume'),
    btnStop: document.getElementById('btn-stop'),
    modeTopics: document.getElementById('mode-topics'),
    modeMonologue: document.getElementById('mode-monologue'),
    modeReader: document.getElementById('mode-reader'),
    inputTheme: document.getElementById('input-theme'),
    inputReaderText: document.getElementById('input-reader-text'),
    monologueInput: document.getElementById('monologue-input'),
    readerInput: document.getElementById('reader-input'),
    statusBadge: document.getElementById('status-badge'),
    currentMode: document.getElementById('current-mode'),
    sessionsContainer: document.getElementById('sessions-container'),
    btnRefreshSessions: document.getElementById('btn-refresh-sessions'),
    audioPlayerContainer: document.getElementById('audio-player-container'),
    audioStream: document.getElementById('audio-stream')
};

// ========== UTILIDADES ==========

/**
 * Muestra una notificación toast
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    const colors = {
        success: 'bg-green-600',
        error: 'bg-red-600',
        info: 'bg-blue-600',
        warning: 'bg-yellow-600'
    };
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };
    
    toast.className = `${colors[type]} text-white px-6 py-4 rounded-lg shadow-2xl transform transition-all duration-300 flex items-center gap-3 max-w-md`;
    toast.innerHTML = `
        <i class="fas ${icons[type]} text-xl"></i>
        <span>${message}</span>
    `;
    
    const container = document.getElementById('toast-container');
    container.appendChild(toast);
    
    // Animación de entrada
    setTimeout(() => toast.classList.add('translate-y-0', 'opacity-100'), 10);
    
    // Auto-remover después de 4 segundos
    setTimeout(() => {
        toast.classList.add('-translate-y-4', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/**
 * Realiza una petición fetch con manejo de errores
 */
async function apiFetch(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.error || 'Error en la petición');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ========== FUNCIONES DE CONTROL ==========

/**
 * Inicia la radio
 */
async function startRadio() {
    try {
        const payload = {
            mode: state.currentMode,
            enable_streaming: true,  // true = streaming web (necesario para Render.com)
            skip_intro: true         // Saltar introducción automáticamente
        };
        
        if (state.currentMode === 'monologue') {
            const theme = elements.inputTheme.value.trim();
            if (!theme) {
                showToast('Por favor ingresa un tema para el monólogo', 'warning');
                elements.inputTheme.focus();
                return;
            }
            payload.theme = theme;
        } else if (state.currentMode === 'reader') {
            const readerText = elements.inputReaderText.value.trim();
            if (!readerText) {
                showToast('Por favor ingresa el texto a leer', 'warning');
                elements.inputReaderText.focus();
                return;
            }
            payload.reader_text = readerText;
        }
        
        const data = await apiFetch('/start', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        showToast(data.message || '¡Radio iniciada!', 'success');
        updateUIState('running');
        startStatusPolling();
        
        // Mostrar reproductor de audio
        showAudioPlayer();
    } catch (error) {
        showToast(`Error al iniciar: ${error.message}`, 'error');
    }
}

/**
 * Pausa la radio
 */
async function pauseRadio() {
    try {
        const data = await apiFetch('/pause', { method: 'POST' });
        showToast(data.message || 'Radio en pausa', 'info');
        updateUIState('paused');
    } catch (error) {
        showToast(`Error al pausar: ${error.message}`, 'error');
    }
}

/**
 * Reanuda la radio
 */
async function resumeRadio() {
    try {
        const data = await apiFetch('/resume', { method: 'POST' });
        showToast(data.message || 'Radio reanudada', 'success');
        updateUIState('running');
    } catch (error) {
        showToast(`Error al reanudar: ${error.message}`, 'error');
    }
}

/**
 * Detiene la radio
 */
async function stopRadio() {
    try {
        const data = await apiFetch('/stop', { method: 'POST' });
        hideAudioPlayer();
        showToast(data.message || 'Radio detenida', 'info');
        updateUIState('stopped');
        stopStatusPolling();
    } catch (error) {
        showToast(`Error al detener: ${error.message}`, 'error');
    }
}

/**
 * Cambia el modo de operación
 */
async function setMode(mode) {
    try {
        const data = await apiFetch('/set_mode', {
            method: 'POST',
            body: JSON.stringify({ mode })
        });
        
        state.currentMode = mode;
        elements.currentMode.textContent = mode.toUpperCase();
        
        // Actualizar UI de botones de modo - todos inactivos primero
        [elements.modeTopics, elements.modeMonologue, elements.modeReader].forEach(btn => {
            btn.style.backgroundColor = '#415A77';
            btn.style.borderColor = '#415A77';
            btn.style.color = '#E0E1DD';
            btn.style.opacity = '0.7';
        });
        
        // Activar el botón seleccionado
        const activeBtn = mode === 'topics' ? elements.modeTopics : 
                         mode === 'monologue' ? elements.modeMonologue : elements.modeReader;
        activeBtn.style.color = '#F5F5F5';
        activeBtn.style.opacity = '1';
        
        // Mostrar/ocultar inputs según modo
        if (mode === 'monologue') {
            elements.monologueInput.classList.remove('hidden');
            elements.readerInput.classList.add('hidden');
        } else if (mode === 'reader') {
            elements.monologueInput.classList.add('hidden');
            elements.readerInput.classList.remove('hidden');
        } else {
            elements.monologueInput.classList.add('hidden');
            elements.readerInput.classList.add('hidden');
        }
        
        showToast(`Modo cambiado a ${mode.toUpperCase()}`, 'info');
    } catch (error) {
        showToast(`Error al cambiar modo: ${error.message}`, 'error');
    }
}

/**
 * Actualiza el estado de la UI según el estado de la radio
 */
function updateUIState(status) {
    state.status = status;
    
    const statusConfig = {
        stopped: {
            label: 'DETENIDO',
            class: 'bg-accent',
            style: 'background-color: #415A77; color: #E0E1DD;',
            buttons: {
                start: false,
                pause: true,
                resume: true,
                stop: true
            }
        },
        running: {
            label: 'ENCENDIDA',
            class: 'bg-green-600 text-white animate-pulse-slow',
            style: '',
            buttons: {
                start: true,
                pause: false,
                resume: true,
                stop: false
            }
        },
        paused: {
            label: 'PAUSADA',
            class: 'bg-yellow-600 text-white',
            style: '',
            buttons: {
                start: true,
                pause: true,
                resume: false,
                stop: false
            }
        },
        generating: {
            label: 'GENERANDO',
            class: 'bg-blue-600 text-white animate-pulse-slow',
            style: '',
            buttons: {
                start: true,
                pause: false,
                resume: true,
                stop: false
            }
        },
        playing: {
            label: 'REPRODUCIENDO',
            class: 'animate-pulse-slow',
            style: 'background-color: #415A77; color: #F5F5F5;',
            buttons: {
                start: true,
                pause: false,  // Habilitar pausa durante reproducción de sesiones
                resume: true,
                stop: false  // false = enabled (poder detener la sesión)
            }
        }
    };
    
    const config = statusConfig[status] || statusConfig.stopped;
    
    // Actualizar badge de estado
    elements.statusBadge.textContent = config.label;
    elements.statusBadge.className = `status-badge px-4 py-2 rounded-full text-sm font-bold ${config.class}`;
    if (config.style) {
        elements.statusBadge.setAttribute('style', config.style);
    }
    
    // Actualizar botones
    elements.btnStart.disabled = config.buttons.start;
    elements.btnPause.disabled = config.buttons.pause;
    elements.btnResume.disabled = config.buttons.resume;
    elements.btnStop.disabled = config.buttons.stop;
}

// ========== SESIONES ==========

/**
 * Carga la lista de sesiones guardadas
 */
async function loadSessions() {
    try {
        const data = await apiFetch('/list_sessions');
        
        if (!data.sessions || data.sessions.length === 0) {
            elements.sessionsContainer.innerHTML = `
                <div class="text-center py-8" style="color: #E0E1DD;">
                    <i class="fas fa-inbox text-5xl mb-4 opacity-50"></i>
                    <p>No hay sesiones guardadas aún</p>
                </div>
            `;
            return;
        }
        
        elements.sessionsContainer.innerHTML = data.sessions.map(session => `
            <div class="rounded-lg p-4 flex items-center justify-between transition" style="background-color: #415A77;">
                <div class="flex-1">
                    <div class="font-bold" style="color: #F5F5F5;">${session.id}</div>
                    <div class="text-sm" style="color: #E0E1DD;">
                        <i class="far fa-calendar mr-1"></i>${session.date || 'Fecha no disponible'}
                        <span class="mx-2">•</span>
                        <i class="fas fa-clock mr-1"></i>${session.duration || 'N/A'}
                        <span class="mx-2">•</span>
                        <i class="fas fa-list-ol mr-1"></i>${session.segments || 0} segmentos
                    </div>
                </div>
                <button 
                    onclick="playSession('${session.id}')"
                    class="font-bold py-2 px-4 rounded-lg transition duration-300 ml-4"
                    style="background-color: #1B263B; color: #F5F5F5;"
                    onmouseover="this.style.opacity='0.8'"
                    onmouseout="this.style.opacity='1'">
                    <i class="fas fa-play mr-2"></i>Reproducir
                </button>
            </div>
        `).join('');
        
    } catch (error) {
        elements.sessionsContainer.innerHTML = `
            <div class="text-center py-8 text-red-400">
                <i class="fas fa-exclamation-triangle text-5xl mb-4"></i>
                <p>Error al cargar sesiones: ${error.message}</p>
            </div>
        `;
    }
}

/**
 * Reproduce una sesión guardada
 */
async function playSession(sessionId) {
    try {
        const data = await apiFetch(`/play_session/${sessionId}`, { method: 'POST' });
        showToast(data.message || `Reproduciendo sesión ${sessionId}`, 'success');
        
        // Mostrar reproductor de audio
        showAudioPlayer();
        
        // Actualizar UI para mostrar que está reproduciendo
        updateUIState('playing');
        startStatusPolling();
    } catch (error) {
        showToast(`Error al reproducir sesión: ${error.message}`, 'error');
    }
}

// ========== POLLING DE ESTADO ==========

/**
 * Inicia el polling del estado del servidor
 */
function startStatusPolling() {
    if (pollingInterval) return;
    
    pollingInterval = setInterval(async () => {
        try {
            const data = await apiFetch('/status');
            
            if (data.status) {
                updateUIState(data.status);
                
                // Detener polling y ocultar reproductor si la radio se detiene
                if (data.status === 'stopped' && !data.is_running) {
                    hideAudioPlayer();
                    stopStatusPolling();
                }
            }
        } catch (error) {
            console.error('Error en polling:', error);
        }
    }, 2000); // Cada 2 segundos
}

/**
 * Detiene el polling del estado
 */
function stopStatusPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

// ========== EVENT LISTENERS ==========

// Botones de control
elements.btnStart.addEventListener('click', startRadio);
elements.btnPause.addEventListener('click', pauseRadio);
elements.btnResume.addEventListener('click', resumeRadio);
elements.btnStop.addEventListener('click', stopRadio);

// Selector de modo
elements.modeTopics.addEventListener('click', () => setMode('topics'));
elements.modeMonologue.addEventListener('click', () => setMode('monologue'));
elements.modeReader.addEventListener('click', () => setMode('reader'));

// Actualizar sesiones
elements.btnRefreshSessions.addEventListener('click', loadSessions);

// ========== INICIALIZACIÓN ==========

/**
 * Inicializa la aplicación
 */
async function init() {
    console.log('🎙️ Radio IA - Inicializando interfaz web...');
    
    // Cargar sesiones
    await loadSessions();
    
    // Verificar estado inicial del servidor
    try {
        const data = await apiFetch('/status');
        if (data.status) {
            updateUIState(data.status);
        }
        if (data.mode) {
            state.currentMode = data.mode;
            elements.currentMode.textContent = data.mode.toUpperCase();
        }
        showToast('Conectado al servidor', 'success');
    } catch (error) {
        showToast('No se pudo conectar al servidor. Asegúrate de que esté ejecutándose.', 'error');
        console.error('Error de conexión:', error);
    }
}

// Funciones de control del reproductor de audio
function showAudioPlayer() {
    elements.audioPlayerContainer.classList.remove('hidden');
    elements.audioStream.load();
    elements.audioStream.play().catch(e => console.log('Autoplay bloqueado:', e));
}

function hideAudioPlayer() {
    elements.audioPlayerContainer.classList.add('hidden');
    elements.audioStream.pause();
    elements.audioStream.currentTime = 0;
}

// Iniciar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Exponer funciones globales para uso desde HTML
window.playSession = playSession;
