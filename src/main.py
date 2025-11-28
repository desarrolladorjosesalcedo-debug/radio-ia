"""
main.py
Punto de entrada principal de la aplicación Radio IA
Inicializa los componentes y arranca el bucle de radio
"""

import sys
import argparse
from core.radio_loop import start_radio, load_config
from core.replay import replay_session, show_session_list, show_session_text


def main():
    """Función principal que inicia la radio IA"""
    parser = argparse.ArgumentParser(
        description="Radio IA - Radio automatizada con inteligencia artificial",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python src/main.py                        # Iniciar radio en vivo
  python src/main.py --list-sessions        # Ver historial de sesiones
  python src/main.py --replay 20251128_143000  # Reproducir sesión
  python src/main.py --show 20251128_143000    # Ver texto de sesión
  python src/main.py --skip-intro            # Iniciar sin introducción
        """
    )
    
    parser.add_argument(
        "--list-sessions",
        action="store_true",
        help="Mostrar lista de sesiones guardadas"
    )
    
    parser.add_argument(
        "--replay",
        metavar="SESSION_ID",
        help="Reproducir una sesión guardada por su ID"
    )
    
    parser.add_argument(
        "--show",
        metavar="SESSION_ID",
        help="Mostrar el texto completo de una sesión"
    )
    
    parser.add_argument(
        "--skip-intro",
        action="store_true",
        help="Iniciar radio sin reproducir introducción"
    )
    
    parser.add_argument(
        "--delay",
        type=float,
        metavar="SECONDS",
        help="Pausa entre segmentos en segundos (default: 2.0)"
    )
    
    args = parser.parse_args()
    
    # Cargar configuración
    config = load_config()
    history_dir = config.get("history_dir", "history")
    
    try:
        # Comando: listar sesiones
        if args.list_sessions:
            show_session_list(history_dir=history_dir)
            return
        
        # Comando: mostrar texto de sesión
        if args.show:
            show_session_text(args.show, history_dir=history_dir)
            return
        
        # Comando: reproducir sesión
        if args.replay:
            delay = args.delay if args.delay is not None else 2.0
            success = replay_session(
                session_id=args.replay,
                delay_seconds=delay,
                history_dir=history_dir
            )
            sys.exit(0 if success else 1)
        
        # Comando por defecto: iniciar radio en vivo
        print("🎙️  Iniciando Radio IA...")
        print("=" * 50)
        delay = args.delay if args.delay is not None else config.get("delay_seconds", 2.0)
        start_radio(
            delay_seconds=delay,
            skip_intro=args.skip_intro
        )
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 50)
        print("🎵 Radio IA finalizada. ¡Hasta pronto!")
        print("=" * 50)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
