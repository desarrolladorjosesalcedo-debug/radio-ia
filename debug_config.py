"""
Debug: Verificar configuración del modo
"""
import yaml
from pathlib import Path

settings_path = Path("config/settings.yaml")

with open(settings_path, 'r', encoding='utf-8') as f:
    settings = yaml.safe_load(f)

print("=== CONFIGURACIÓN CARGADA ===")
print(f"radio.mode: {settings.get('radio', {}).get('mode')}")
print(f"radio.monologue_theme: {settings.get('radio', {}).get('monologue_theme')}")
print()
print("=== CONFIG DICT ===")
mode = settings.get("radio", {}).get("mode", "topics")
monologue_theme = settings.get("radio", {}).get("monologue_theme", "inteligencia artificial")
print(f"mode: {mode}")
print(f"monologue_theme: {monologue_theme}")
