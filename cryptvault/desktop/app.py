"""
CryptVault Desktop App entry point.

The UI is a local single-page app rendered by trading-vue-js. It runs in a
native window when ``pywebview`` is installed, and falls back to the default
browser otherwise — same app either way.
"""

from __future__ import annotations

import logging
import sys
import threading
import webbrowser

logger = logging.getLogger(__name__)


def launch_app(open_window: bool = True) -> None:
    """Start the local server and open the CryptVault chart."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        from .server import serve, vendor_asset
    except ImportError as e:
        print(f"[CryptVault] Missing dependency: {e}")
        print("Run:  pip install -r requirements.txt")
        sys.exit(1)

    try:
        httpd = serve()
        url = "http://127.0.0.1:%d/" % httpd.server_address[1]
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        logger.info("CryptVault desktop running at %s", url)

        # Pull the chart bundles before the window opens, so a slow first
        # connection doesn't show a blank page.
        for asset in ("vue.min.js", "trading-vue.min.js"):
            try:
                vendor_asset(asset)
            except Exception as e:
                logger.warning("Could not pre-fetch %s: %s", asset, e)

        if not open_window:
            httpd.serve_forever()
            return

        if not _native_window(url):
            webbrowser.open(url)
            print(f"[CryptVault] Opened in your browser: {url}")
            print("[CryptVault] Press Ctrl+C to quit.")
            threading.Event().wait()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.critical("Fatal error launching desktop app: %s", e, exc_info=True)
        sys.exit(1)


def _native_window(url: str) -> bool:
    """Open a native webview window. Returns False if pywebview is unavailable."""
    try:
        import webview
    except ImportError:
        return False
    webview.create_window("CryptVault", url, width=1500, height=900,
                          background_color="#0b0e14")
    webview.start()
    return True


if __name__ == "__main__":
    launch_app()
