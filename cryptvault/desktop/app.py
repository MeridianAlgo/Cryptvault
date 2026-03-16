"""
CryptVault Desktop App entry point.
"""

import logging
import sys


def launch_app() -> None:
    """Launch the CryptVault desktop application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        from .main_window import MainWindow
        app = MainWindow()
        app.run()
    except ImportError as e:
        print(f"[CryptVault] Missing dependency: {e}")
        print("Run:  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logging.critical("Fatal error launching desktop app: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    launch_app()
