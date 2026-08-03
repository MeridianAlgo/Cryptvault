"""
Local HTTP server backing the desktop chart.

Three routes, no framework:
    GET /                     the single-page UI
    GET /vendor/<file>        Vue 2 + trading-vue-js, downloaded once and cached
    GET /api/analyze?...      JSON analysis payload

Binds to 127.0.0.1 only — nothing is exposed off the machine.
"""

from __future__ import annotations

import json
import logging
import socket
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import api

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
INDEX = HERE / "index.html"

# Pinned so a CDN release can never change the chart under us.
VENDOR = {
    "vue.min.js": "https://unpkg.com/vue@2.6.14/dist/vue.min.js",
    "trading-vue.min.js": "https://unpkg.com/trading-vue-js@1.0.2/dist/trading-vue.min.js",
}
CACHE_DIR = Path.home() / ".cryptvault" / "vendor"


def vendor_asset(name: str) -> bytes:
    """Return a vendored JS bundle, downloading it on first use."""
    url = VENDOR.get(name)
    if url is None:
        raise KeyError(name)
    path = CACHE_DIR / name
    if not path.exists() or path.stat().st_size == 0:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("Downloading %s ...", name)
        with urllib.request.urlopen(url, timeout=30) as r:   # noqa: S310 - pinned https URLs
            path.write_bytes(r.read())
    return path.read_bytes()


class _Handler(BaseHTTPRequestHandler):
    server_version = "CryptVault"

    def log_message(self, fmt, *args):          # quieter than the stdlib default
        logger.debug("%s - %s", self.address_string(), fmt % args)

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj) -> None:
        self._send(code, json.dumps(obj).encode(), "application/json")

    def do_GET(self) -> None:                   # noqa: N802 - stdlib naming
        route = urlparse(self.path)
        path = route.path

        try:
            if path in ("/", "/index.html"):
                self._send(200, INDEX.read_bytes(), "text/html; charset=utf-8")

            elif path.startswith("/vendor/"):
                self._send(200, vendor_asset(path[len("/vendor/"):]),
                           "application/javascript; charset=utf-8")

            elif path == "/api/meta":
                from ..__version__ import __version__
                self._json(200, {"version": __version__,
                                 "timeframes": list(api.TIMEFRAMES),
                                 "default": api.DEFAULT_TF})

            elif path == "/api/analyze":
                q = parse_qs(route.query)
                symbol = (q.get("symbol") or [""])[0]
                tf = (q.get("tf") or [api.DEFAULT_TF])[0]
                self._json(200, api.analyze(symbol, tf))

            else:
                self._json(404, {"error": "not found"})

        except KeyError:
            self._json(404, {"error": "unknown asset"})
        except ValueError as e:
            self._json(400, {"error": str(e)})
        except BrokenPipeError:
            pass                                # client navigated away mid-response
        except Exception as e:
            logger.error("Request %s failed: %s", self.path, e, exc_info=True)
            self._json(500, {"error": str(e)})


def serve(port: int = 0) -> ThreadingHTTPServer:
    """Start the server on localhost. Port 0 picks a free one."""
    httpd = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    httpd.daemon_threads = True
    return httpd


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
