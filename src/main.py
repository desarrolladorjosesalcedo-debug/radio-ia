"""
main.py
Punto de entrada principal de la aplicación Radio IA
Inicializa los componentes y arranca el bucle de radio
"""

import sys
from core.radio_loop import start_radio


def main():
    """Función principal que inicia la radio IA"""
    try:
        print("🎙️  Iniciando Radio IA...")
        print("=" * 50)
        start_radio()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 50)
        print("🎵 Radio IA finalizada. ¡Hasta pronto!")
        print("=" * 50)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
