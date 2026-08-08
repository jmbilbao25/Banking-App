"""Render .excalidraw -> PNG using a locally bundled Excalidraw + real fonts.

Usage: uv run python render.py <file.excalidraw> [more.excalidraw ...] [--scale 2]
"""
from __future__ import annotations

import argparse
import contextlib
import functools
import http.server
import json
import socket
import socketserver
import sys
import threading
from pathlib import Path

WEB = Path(__file__).parent / "web"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@contextlib.contextmanager
def serve(directory: Path):
    handler = functools.partial(Quiet, directory=str(directory))
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.socket.getsockname()[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            yield port
        finally:
            httpd.shutdown()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("--scale", "-s", type=int, default=2)
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    with serve(WEB) as port, sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1600, "height": 1200},
            device_scale_factor=args.scale,
        )
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)[:300]))
        page.goto(f"http://127.0.0.1:{port}/index.html")
        page.wait_for_function("window.__moduleReady === true", timeout=60000)

        failed = False
        for inp in args.inputs:
            if not inp.exists():
                print(f"ERROR: not found: {inp}", file=sys.stderr)
                failed = True
                continue
            data = json.loads(inp.read_text(encoding="utf-8"))
            page.evaluate("window.__renderComplete = false; window.__renderError = null;")
            res = page.evaluate("(d) => window.renderDiagram(d)", data)
            if not res or not res.get("success"):
                msg = (res or {}).get("error", "unknown")
                print(f"ERROR rendering {inp.name}: {msg}", file=sys.stderr)
                failed = True
                continue
            page.wait_for_function("window.__renderComplete === true", timeout=60000)
            page.wait_for_timeout(500)
            svg = page.query_selector("#root svg")
            if svg is None:
                print(f"ERROR: no svg for {inp.name}", file=sys.stderr)
                failed = True
                continue
            out = inp.with_suffix(".png")
            svg.screenshot(path=str(out))
            print(f"{out}  ({res.get('width')}x{res.get('height')})")

        if errors:
            print("PAGE ERRORS:", *errors[:5], sep="\n  ", file=sys.stderr)
        browser.close()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
