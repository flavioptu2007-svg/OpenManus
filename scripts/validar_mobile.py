#!/usr/bin/env python3
"""Valida a experiência mobile de todas as páginas HTML do portal com Playwright.

Roda uma bateria de verificação em viewport de celular (padrão 390x844) contra
cada página servida pelo portal, medindo:

  - Erros de JavaScript (pageerror + console.error)
  - Overflow horizontal (scrollWidth > innerWidth => rolagem lateral indesejada)
  - Recursos quebrados (respostas HTTP >= 400, exceto favicon opcional)
  - Ausência da meta tag viewport (aviso, não falha)

Uso:
    python3 scripts/validar_mobile.py
    python3 scripts/validar_mobile.py --base-url http://192.168.15.17:8765
    python3 scripts/validar_mobile.py --only jogo_bingo --json relatorio.json
    python3 scripts/validar_mobile.py --no-favicon-ok   # favicon 404 vira falha

Requisitos:
    - Playwright + Chromium no venv do projeto (.venv)
    - Portal no ar (systemctl --user status portal-projetos.service)

Exit codes:
    0 = todas as páginas OK
    1 = pelo menos uma página falhou (erro JS, overflow ou 404)
    2 = erro de infraestrutura (portal offline, Chromium ausente, etc.)
"""

import argparse
import asyncio
import glob
import json
import os
import sys
import urllib.error
import urllib.request


try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERRO: playwright não está instalado no ambiente.", file=sys.stderr)
    print(
        "Instale com:  uv pip install --python .venv/bin/python playwright",
        file=sys.stderr,
    )
    sys.exit(2)

# Diretório padrão do portal (mesmo usado pelo serviço systemd).
DEFAULT_DIR = os.environ.get("PORTAL_DIR", "/home/flavio/portal_projetos")
DEFAULT_BASE = os.environ.get("PORTAL_BASE", "http://localhost:8765")
DEFAULT_VIEWPORT = "390x844"

# Caminhos de Chromium do Playwright, por ordem de preferência.
CHROME_CANDIDATES = (
    "~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome",
    "~/.cache/ms-playwright/chromium_headless_shell-*/chrome-linux64/headless_shell",
    "~/.cache/ms-playwright/chromium-*/chrome-linux/chrome",
)


def resolver_chromium():
    """Retorna o caminho de um executável Chromium, ou None se não achar."""
    for pattern in CHROME_CANDIDATES:
        matches = sorted(glob.glob(os.path.expanduser(pattern)))
        if matches:
            return matches[-1]  # versão mais recente
    return None


async def checar_pagina(page, base_url, nome, ignorar_favicon, timeout_ms):
    """Abre uma página e coleta problemas. Retorna dict com o resultado."""
    erros_js = []
    falhas_http = []

    def on_pageerror(exc):
        erros_js.append(f"pageerror: {str(exc)[:160]}")

    def on_console(msg):
        if msg.type == "error":
            txt = msg.text.strip()
            # Erros de recurso já são capturados em falhas_http; evita duplicar
            # mensagens genéricas de "Failed to load resource".
            if "Failed to load resource" not in txt:
                erros_js.append(f"console: {txt[:160]}")

    async def on_response(resp):
        if resp.status >= 400:
            url = resp.url
            if ignorar_favicon and "favicon" in url:
                return
            falhas_http.append(f"{resp.status} {url}")

    async def on_request_failed(req):
        url = req.url
        if ignorar_favicon and "favicon" in url:
            return
        if "data:" in url:
            return
        falhas_http.append(f"falha de rede: {req.failure}")

    page.on("pageerror", on_pageerror)
    page.on("console", on_console)
    page.on("response", on_response)
    page.on("requestfailed", on_request_failed)

    resultado = {
        "pagina": nome,
        "ok": True,
        "erros_js": [],
        "falhas_http": [],
        "overflow": False,
        "scroll_width": 0,
        "inner_width": 0,
        "sem_viewport": False,
        "tempo_ms": 0,
    }

    try:
        await page.goto(f"{base_url}/{nome}", wait_until="load", timeout=timeout_ms)
        await page.wait_for_timeout(600)

        # Overflow horizontal real (documento mais largo que a janela).
        dims = await page.evaluate(
            """() => ({
                scroll: document.documentElement.scrollWidth,
                inner: window.innerWidth
            })"""
        )
        resultado["scroll_width"] = dims["scroll"]
        resultado["inner_width"] = dims["inner"]
        resultado["overflow"] = dims["scroll"] > dims["inner"]

        # Meta viewport ausente = aviso (layout pode não escalar no celular).
        tem_viewport = await page.evaluate(
            "() => !!document.querySelector('meta[name=viewport]')"
        )
        resultado["sem_viewport"] = not tem_viewport

    except Exception as exc:  # timeout de navegação, página travada, etc.
        erros_js.append(f"falha ao carregar: {str(exc)[:160]}")

    # Desliga os listeners antes de descartar a página.
    page.remove_listener("pageerror", on_pageerror)
    page.remove_listener("console", on_console)
    page.remove_listener("response", on_response)
    page.remove_listener("requestfailed", on_request_failed)

    resultado["erros_js"] = erros_js
    resultado["falhas_http"] = falhas_http
    resultado["ok"] = not erros_js and not falhas_http and not resultado["overflow"]
    return resultado


def portal_no_ar(base_url, timeout=5):
    """Verificação rápida se o portal responde (pré-flight de infraestrutura)."""
    url = base_url.rstrip("/") + "/index.html"
    try:
        with urllib.request.urlopen(url, timeout=timeout):
            return True
    except Exception:
        return False


async def executar_bateria(args):
    paginas = sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(args.dir, "*.html"))
    )
    if not paginas:
        print(f"ERRO: nenhum *.html encontrado em {args.dir}", file=sys.stderr)
        return 2

    if args.only:
        paginas = [p for p in paginas if args.only in p]
        if not paginas:
            print(
                f"Nenhuma página corresponde ao filtro '{args.only}'.", file=sys.stderr
            )
            return 2

    w, h = (int(x) for x in args.viewport.lower().split("x"))
    chrome = resolver_chromium()
    if not chrome:
        print("ERRO: não encontrei executável Chromium do Playwright.", file=sys.stderr)
        print(
            "Instale com:  uv pip install --python .venv/bin/python playwright && ./.venv/bin/python -m playwright install chromium",
            file=sys.stderr,
        )
        return 2

    if not portal_no_ar(args.base_url):
        print(f"ERRO: o portal não responde em {args.base_url}", file=sys.stderr)
        print(
            "Verifique o serviço:  systemctl --user status portal-projetos.service",
            file=sys.stderr,
        )
        return 2

    print(f"→ {len(paginas)} página(s) · viewport {w}x{h} · Chromium: {chrome}")
    print(f"→ Base: {args.base_url}  (páginas de: {args.dir})\n")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                executable_path=chrome,
                args=["--no-sandbox"],
                headless=not args.headed,
            )
        except Exception as exc:
            print(f"ERRO ao iniciar Chromium: {exc}", file=sys.stderr)
            return 2

        context = await browser.new_context(
            viewport={"width": w, "height": h},
            is_mobile=args.mobile,
            device_scale_factor=args.dsf,
        )

        try:
            resultados = []
            for i, nome in enumerate(paginas, 1):
                page = await context.new_page()
                res = await checar_pagina(
                    page, args.base_url, nome, args.no_favicon_ok, args.timeout
                )
                await page.close()

                status = "✅" if res["ok"] else "❌"
                detalhe = []
                if res["erros_js"]:
                    detalhe.append(f"{len(res['erros_js'])} erro(s) JS")
                if res["falhas_http"]:
                    detalhe.append(f"{len(res['falhas_http'])} 404/erro(s)")
                if res["overflow"]:
                    detalhe.append(
                        f"overflow {res['scroll_width']}>{res['inner_width']}px"
                    )
                if res["sem_viewport"]:
                    detalhe.append("sem meta viewport")
                extra = (" · " + ", ".join(detalhe)) if detalhe else ""
                print(f"  [{i:>2}/{len(paginas)}] {status} {nome}{extra}")
                resultados.append(res)
        finally:
            await browser.close()

    # ----- Relatório final -----
    ok_count = sum(1 for r in resultados if r["ok"])
    falhas = [r for r in resultados if not r["ok"]]
    avisos = [r for r in resultados if r["ok"] and r["sem_viewport"]]

    print()
    print("=" * 60)
    print(f"RESULTADO: {ok_count}/{len(resultados)} páginas OK")

    if avisos:
        print(f"\n⚠ Avisos (sem meta viewport — layout pode não escalar):")
        for a in avisos:
            print(f"  - {a['pagina']}")

    if falhas:
        print(f"\n❌ Falhas ({len(falhas)}):")
        for f in falhas:
            print(f"  - {f['pagina']}")
            for e in f["erros_js"][:3]:
                print(f"      JS: {e}")
            for h in f["falhas_http"][:3]:
                print(f"      HTTP: {h}")
            if f["overflow"]:
                print(
                    f"      overflow: scrollWidth={f['scroll_width']} > innerWidth={f['inner_width']}"
                )

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "viewport": args.viewport,
                    "base_url": args.base_url,
                    "total": len(resultados),
                    "ok": ok_count,
                    "falhas": [r for r in resultados if not r["ok"]],
                    "avisos_sem_viewport": [r["pagina"] for r in avisos],
                    "resultados": resultados,
                },
                fh,
                ensure_ascii=False,
                indent=2,
            )
        print(f"\n📄 Relatório JSON salvo em: {args.json}")

    return 0 if not falhas else 1


def main():
    parser = argparse.ArgumentParser(
        description="Bateria de validação mobile (Playwright) das páginas do portal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE,
        help=f"URL base do portal (padrão: {DEFAULT_BASE})",
    )
    parser.add_argument(
        "--dir",
        default=DEFAULT_DIR,
        help=f"Diretório com os HTMLs (padrão: {DEFAULT_DIR})",
    )
    parser.add_argument(
        "--viewport",
        default=DEFAULT_VIEWPORT,
        help="Tamanho da janela WxH (padrão: 390x844)",
    )
    parser.add_argument(
        "--dsf", type=float, default=1.0, help="Device Scale Factor (padrão: 1.0)"
    )
    parser.add_argument(
        "--no-mobile",
        action="store_false",
        dest="mobile",
        help="Desliga is_mobile (emulação mobile do navegador)",
    )
    parser.add_argument(
        "--only", default=None, help="Testa apenas páginas cujo nome contém este texto"
    )
    parser.add_argument(
        "--no-favicon-ok",
        action="store_true",
        help="Trata 404 de favicon como falha (padrão: ignora)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15000,
        help="Timeout de carga por página em ms (padrão: 15000)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Abre o navegador com janela visível (debug)",
    )
    parser.add_argument(
        "--json", default=None, help="Caminho para salvar relatório JSON detalhado"
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(executar_bateria(args)))


if __name__ == "__main__":
    main()
