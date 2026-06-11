#!/usr/bin/env python3
"""Serve the committed docs/ folder under /docs/python-switch.

This mimics the production nginx layout (site hosted at a subpath, not the domain
root) so a local preview catches any absolute-path asset bugs before publishing.
"""

from __future__ import annotations

import functools
import http.server
import socketserver
from pathlib import Path

PREFIX = '/docs/python-switch'
PORT = 8099
ROOT = Path(__file__).resolve().parent.parent / 'docs'


class DocsHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        clean = path.split('?', 1)[0].split('#', 1)[0]
        if clean.startswith(PREFIX):
            path = clean[len(PREFIX) :] or '/'
        return super().translate_path(path)

    def send_head(self):
        # Redirect the bare prefix (and root) to the canonical trailing-slash URL.
        if self.path in ('/', PREFIX):
            self.send_response(302)
            self.send_header('Location', PREFIX + '/')
            self.end_headers()
            return None
        return super().send_head()


class ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True


def main() -> None:
    if not ROOT.is_dir():
        raise SystemExit(f'Run scripts/build_docs.py first; {ROOT} is missing')

    handler = functools.partial(DocsHandler, directory=str(ROOT))
    with ReusableServer(('127.0.0.1', PORT), handler) as httpd:
        print(f'-> http://127.0.0.1:{PORT}{PREFIX}/  (Ctrl+C to stop)')
        httpd.serve_forever()


if __name__ == '__main__':
    main()
