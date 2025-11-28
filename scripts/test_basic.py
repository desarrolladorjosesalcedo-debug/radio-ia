"""
test_basic.py
Script de prueba básico para verificar que todos los componentes funcionan.
Ejecutar antes del primer test completo de la radio.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Verifica que todos los módulos se pueden importar"""
    print("🔍 Verificando imports...")
    
    try:
        from core import topics, prompt, radio_loop
        from llm import ollama_client
        from tts import piper_tts
        from utils import audio_player
        print("✅ Todos los imports exitosos")
        return True
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False


def test_dependencies():
    """Verifica que las dependencias externas están disponibles"""
    print("\n🔍 Verificando dependencias externas...")
    
    from llm.ollama_client import check_ollama_available
    from tts.piper_tts import check_piper_available
    from utils.audio_player import check_ffplay_available
    
    ollama_ok = check_ollama_available()
    piper_ok = check_piper_available()
    ffplay_ok = check_ffplay_available()
    
    all_ok = ollama_ok and piper_ok and ffplay_ok
    
    if all_ok:
        print("✅ Todas las dependencias disponibles")
    else:
        print("⚠️  Algunas dependencias faltan")
    
    return all_ok


def test_config():
    """Verifica que la configuración se puede cargar"""
    print("\n🔍 Verificando configuración...")
    
    try:
        from core.radio_loop import load_config
        config = load_config()
        print(f"✅ Configuración cargada: {len(config)} parámetros")
        print(f"   Modelo LLM: {config.get('model_name')}")
        print(f"   Modelo TTS: {config.get('model_path')}")
        return True
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False


def test_topics():
    """Verifica el sistema de temas"""
    print("\n🔍 Verificando sistema de temas...")
    
    try:
        from core.topics import get_random_topic, get_topics_count
        
        count = get_topics_count()
        topic = get_random_topic()
        
        print(f"✅ Sistema de temas funcionando")
        print(f"   Temas disponibles: {count}")
        print(f"   Tema de prueba: '{topic}'")
        return True
    except Exception as e:
        print(f"❌ Error en temas: {e}")
        return False


def test_prompt():
    """Verifica el generador de prompts"""
    print("\n🔍 Verificando generador de prompts...")
    
    try:
        from core.prompt import build_prompt
        
        prompt = build_prompt("programación", duration_seconds=15)
        
        print(f"✅ Generador de prompts funcionando")
        print(f"   Longitud del prompt: {len(prompt)} caracteres")
        return True
    except Exception as e:
        print(f"❌ Error en prompts: {e}")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("🧪 RADIO IA - PRUEBAS BÁSICAS")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Dependencias", test_dependencies()))
    results.append(("Configuración", test_config()))
    results.append(("Temas", test_topics()))
    results.append(("Prompts", test_prompt()))
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_pass = all(r for _, r in results)
    
    print("=" * 60)
    if all_pass:
        print("🎉 TODAS LAS PRUEBAS PASARON")
        print("✅ El sistema está listo para ejecutar")
        print("\nEjecuta la radio con:")
        print("  python src/main.py")
    else:
        print("⚠️  ALGUNAS PRUEBAS FALLARON")
        print("Revisa los errores antes de ejecutar la radio")
    print("=" * 60)
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
