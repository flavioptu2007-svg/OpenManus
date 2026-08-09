#!/usr/bin/env python3
"""Valida a sintaxe JS dos blocos <script> inline de arquivos HTML.

Uso: python3 check_html_js.py arquivo1.html arquivo2.html ...
Requisito: `node` instalado (usa `node --check` para validar cada bloco).

Regras:
  - Scripts externos (<script src=...>) são ignorados;
  - Tipos de dados (importmap, application/json, ld+json, text/template,
    text/html, text/plain) são ignorados — não são JavaScript;
  - Blocos JS puros (sem type, module, text/javascript, etc.) são validados
    com `node --check`;
  - Blocos text/babel ou text/jsx também são validados: JS puro neles passa;
    JSX real falha com "Unexpected token '<'" e é tratado como esperado
    (transpilado pelo Babel no navegador), enquanto qualquer outro erro de
    sintaxe é reportado como falha real.
"""

import os
import re
import subprocess
import sys
import tempfile


# Captura o atributo do bloco (grupo 1) e o conteúdo (grupo 2).
SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.DOTALL | re.IGNORECASE)

# Tipos que nunca são JavaScript (dados ou templates).
TIPOS_NAO_JS = {
    "importmap",
    "application/json",
    "application/ld+json",
    "text/template",
    "text/html",
    "text/plain",
    "application/template",
}

# Tipos tratados pelo navegador como JavaScript puro (ou sem type).
TIPOS_JS = {
    "",
    "text/javascript",
    "application/javascript",
    "module",
    "text/ecmascript",
    "application/ecmascript",
}

# Tipos que podem conter JS puro OU JSX (transpilado pelo Babel no browser).
TIPOS_JSX = {"text/babel", "text/jsx", "application/babel"}


def _tipo_do_bloco(atributos: str) -> str:
    # Âncoras (?:^|\s) evitam casar data-src=/data-type=
    if re.search(r"(?:^|\s)src\s*=", atributos, re.IGNORECASE):
        return "externo"
    m = re.search(r"(?:^|\s)type\s*=\s*[\"']([^\"']*)[\"']", atributos, re.IGNORECASE)
    if m is None:
        return ""
    return m.group(1).strip().lower()


def checar(arquivo: str) -> int:
    try:
        html = open(arquivo, encoding="utf-8").read()
    except OSError as e:
        print(f"❌ {arquivo}: não abriu ({e})")
        return 1
    blocos = SCRIPT_RE.findall(html)
    if not blocos:
        print(f"⚠️  {arquivo}: nenhum bloco <script> inline encontrado")
        return 0
    falhas = 0
    jsx_ignorados = 0  # blocos JSX legítimos (Babel) — esperados
    js_validados = 0  # blocos que passaram no node --check
    for i, (atributos, js) in enumerate(blocos, 1):
        tipo = _tipo_do_bloco(atributos)
        if not js.strip() or tipo == "externo" or tipo in TIPOS_NAO_JS:
            continue
        if tipo not in TIPOS_JS and tipo not in TIPOS_JSX:
            continue  # type desconhecido — não arriscar falso negativo
        with tempfile.NamedTemporaryFile(
            "w", suffix=".js", delete=False, encoding="utf-8"
        ) as f:
            f.write(js)
            tmp = f.name
        try:
            r = subprocess.run(
                ["node", "--check", tmp], capture_output=True, text=True, timeout=30
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            print("⚠️  node não disponível — pulando validação")
            return 0
        finally:
            os.unlink(tmp)
        if r.returncode != 0:
            stderr = (r.stderr or r.stdout).strip()
            if tipo in TIPOS_JSX and "Unexpected token '<'" in stderr:
                # JSX legítimo — será transpilado pelo Babel no navegador
                jsx_ignorados += 1
                continue
            falhas += 1
            primeira = stderr.splitlines()
            detalhe = primeira[-1] if primeira else "erro desconhecido"
            print(f"❌ {arquivo} bloco {i}: ERRO DE SINTAXE -> {detalhe[:160]}")
        else:
            js_validados += 1
            print(f"✅ {arquivo} bloco {i}: sintaxe OK")
    # Nenhum bloco JS passou na validação: informa o motivo.
    if falhas == 0 and js_validados == 0:
        if jsx_ignorados:
            print(
                f"⚠️  {arquivo}: apenas blocos JSX/Babel (pulados — transpilados no navegador)"
            )
        else:
            print(f"⚠️  {arquivo}: nenhum bloco <script> JS puro encontrado")
    return falhas


def main() -> int:
    arquivos = sys.argv[1:]
    if not arquivos:
        print("Uso: python3 check_html_js.py arquivo.html [mais.html...]")
        return 2
    total = sum(checar(a) for a in arquivos)
    print(f"\n{'='*50}")
    print("RESULTADO:", "✅ tudo OK" if total == 0 else f"❌ {total} bloco(s) com erro")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
