#!/usr/bin/env python3
"""
Cobalt Proxy — ponte local para a API do cobalt.tools
======================================================
Resolve o bloqueio de CORS da instância oficial (api.cobalt.tools):
o navegador conversa com este proxy (localhost), que conversa com o cobalt.

Uso:
    python3 cobalt_proxy.py                 # porta 8099, upstream api.cobalt.tools
    COBALT_API=https://instancia.exemplo python3 cobalt_proxy.py
    python3 cobalt_proxy.py 9000            # porta customizada

Endpoints:
    POST /api          → encaminha JSON para a API do cobalt
    GET  /tunnel?url=  → baixa/encaminha o arquivo (stream binário)
    GET  /health       → json {ok: true, upstream: ...}
    OPTIONS *          → CORS preflight
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


UPSTREAM = os.environ.get("COBALT_API", "https://api.cobalt.tools").rstrip("/")
PORT = (
    int(sys.argv[1])
    if len(sys.argv) > 1
    else int(os.environ.get("COBALT_PORT", "8099"))
)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization, X-API-Key",
    "Access-Control-Max-Age": "86400",
}


def send_json(handler, status: int, obj: dict) -> None:
    body = json.dumps(obj).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    for k, v in CORS.items():
        handler.send_header(k, v)
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print(f"[cobalt-proxy] {self.address_string()} {fmt % args}", flush=True)

    # ---------- CORS preflight ----------
    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in CORS.items():
            self.send_header(k, v)
        self.send_header("Content-Length", "0")
        self.end_headers()

    # ---------- health / info da instância / túnel ----------
    def do_GET(self):
        if self.path == "/health":
            return send_json(
                self, 200, {"ok": True, "upstream": UPSTREAM, "port": PORT}
            )
        if self.path.startswith("/tunnel"):
            return self._stream_file()
        if self.path in ("/info", "/"):
            # GET / do upstream: info da instância ({cobalt:{version,services}})
            try:
                with urllib.request.urlopen(
                    urllib.request.Request(
                        UPSTREAM + "/",
                        headers={"User-Agent": UA, "Accept": "application/json"},
                    ),
                    timeout=15,
                ) as r:
                    body = r.read()
                    data = json.loads(body)
                    return send_json(self, 200, data)
            except Exception as e:
                return send_json(
                    self,
                    502,
                    {
                        "status": "error",
                        "error": {"code": "api.upstream", "context": str(e)},
                    },
                )
        return send_json(
            self, 404, {"status": "error", "error": {"code": "api.notfound"}}
        )

    # ---------- POST /session (JWT/turnstile) ----------
    def _session(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        cab = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": UA,
            "Origin": "http://localhost",
            "Referer": "http://localhost/",
        }
        for h in ("cf-turnstile-response", "Authorization"):
            v = self.headers.get(h)
            if v:
                cab[h] = v
        try:
            with urllib.request.urlopen(
                urllib.request.Request(
                    UPSTREAM + "/session", data=raw, headers=cab, method="POST"
                ),
                timeout=30,
            ) as r:
                return send_json(self, 200, json.loads(r.read()))
        except urllib.error.HTTPError as e:
            return send_json(
                self,
                200,
                {"status": "error", "error": {"code": f"api.session.http.{e.code}"}},
            )
        except Exception as e:
            return send_json(
                self,
                502,
                {
                    "status": "error",
                    "error": {"code": "api.session", "context": str(e)},
                },
            )

    # ---------- POST /api e /session ----------
    def do_POST(self):
        path = self.path.rstrip("/")
        if path == "/session":
            return self._session()
        if path not in ("/api", ""):
            return send_json(
                self, 404, {"status": "error", "error": {"code": "api.notfound"}}
            )
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            json.loads(raw)  # valida JSON antes de encaminhar
        except Exception:
            return send_json(
                self, 400, {"status": "error", "error": {"code": "api.invalid.request"}}
            )

        cab = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": UA,
            "Origin": "http://localhost",
            "Referer": "http://localhost/",
        }
        auth = self.headers.get("Authorization") or self.headers.get("X-Api-Key")
        if auth:
            cab["Authorization"] = auth
        req = urllib.request.Request(
            UPSTREAM + "/", data=raw, headers=cab, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
                try:
                    data = json.loads(body)
                    if data.get("status") == "error":
                        # reencaminha o erro do upstream para o tool traduzir
                        return send_json(self, 200, data)
                    # tunnel local: se o upstream devolver url de tunnel,
                    # reescrevemos para passar por este proxy (CORS garantido)
                    if data.get("status") in ("tunnel",) and data.get("url"):
                        data["url"] = (
                            f"http://localhost:{PORT}/tunnel?url="
                            + urllib.parse.quote(data["url"], safe="")
                        )
                    if data.get("status") == "local-processing":
                        data["tunnel"] = [
                            f"http://localhost:{PORT}/tunnel?url="
                            + urllib.parse.quote(u, safe="")
                            for u in (data.get("tunnel") or [])
                        ]
                    return send_json(self, 200, data)
                except Exception:
                    return send_json(
                        self,
                        200,
                        {"status": "tunnel", "url": body.decode(errors="replace")},
                    )
        except urllib.error.HTTPError as e:
            return send_json(
                self, 200, {"status": "error", "error": {"code": f"api.http.{e.code}"}}
            )
        except Exception as e:
            return send_json(
                self,
                502,
                {
                    "status": "error",
                    "error": {"code": "api.upstream", "context": str(e)},
                },
            )

    # ---------- túnel de arquivo ----------
    def _stream_file(self):
        from urllib.parse import parse_qs, urlparse

        qs = parse_qs(urlparse(self.path).query)
        target = qs.get("url", [""])[0]
        if not target:
            return send_json(
                self, 400, {"status": "error", "error": {"code": "api.tunnel.missing"}}
            )
        cab = {"User-Agent": UA}
        auth = self.headers.get("Authorization")
        if auth:
            cab["Authorization"] = auth
        req = urllib.request.Request(target, headers=cab)
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    r.headers.get("Content-Type", "application/octet-stream"),
                )
                self.send_header("Content-Length", r.headers.get("Content-Length", ""))
                fname = ""
                cd = r.headers.get("Content-Disposition", "")
                if "filename=" in cd:
                    fname = cd.split("filename=")[-1].strip('"').split(";")[0]
                if fname:
                    self.send_header(
                        "Content-Disposition", f'attachment; filename="{fname}"'
                    )
                for k, v in CORS.items():
                    self.send_header(k, v)
                self.end_headers()
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except Exception as e:
            return send_json(
                self,
                502,
                {
                    "status": "error",
                    "error": {"code": "api.tunnel.failed", "context": str(e)},
                },
            )


if __name__ == "__main__":
    print(f"⬡ Cobalt Proxy rodando em http://localhost:{PORT}", flush=True)
    print(f"⬡ Upstream: {UPSTREAM}", flush=True)
    print(
        "   No tool, escolha a instância 'Proxy local'. Ctrl+C para parar.", flush=True
    )
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
