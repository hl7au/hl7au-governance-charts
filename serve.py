#!/usr/bin/env python3
"""Local dev server for the chart endpoints.

    python serve.py                 # http://127.0.0.1:8000
    python serve.py --port 9000

Edits to governance.md are picked up on the next request — no restart.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.service import Renderer

ROOT = Path(__file__).parent


def make_handler(renderer: Renderer) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "hl7au-charts"

        def do_GET(self) -> None:  # noqa: N802 - stdlib naming
            url = urlparse(self.path)
            response = renderer.handle(url.path, url.query,
                                       if_none_match=self.headers.get("If-None-Match"))
            payload = response.body.encode("utf-8")
            self.send_response(response.status)
            for key, value in response.headers("no-store").items():
                self.send_header(key, value)
            if response.status != 304:
                self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            if response.status != 304 and self.command != "HEAD":
                self.wfile.write(payload)

        def log_message(self, fmt: str, *args) -> None:
            print(f"{self.address_string()} {fmt % args}")

    return Handler


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--source", type=Path, default=ROOT / "governance.md")
    args = ap.parse_args()

    server = ThreadingHTTPServer((args.host, args.port),
                                 make_handler(Renderer(args.source)))
    print(f"http://{args.host}:{args.port}/  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
