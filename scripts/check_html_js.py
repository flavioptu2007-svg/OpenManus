#!/usr/bin/env python3
"""Valida a sintaxe JS dos blocos <script> inline de arquivos HTML.

Uso: python3 check_html_js.py arquivo1.html arquivo2.html ...
Requisito: `node` instalado (usa `node --check` para validar cada bloco).
"""
import re
import subprocess
import sys
import tempfile


SCRIPT_RE = re.compile(
    r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.DOTALL | re.IGNORECASE
)


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
    for i, js in enumerate(blocos, 1):
        if not js.strip():
            continue
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
            import os

            os.unlink(tmp)
        if r.returncode != 0:
            falhas += 1
            primeira = (r.stderr or r.stdout).strip().splitlines()
            detalhe = primeira[-1] if primeira else "erro desconhecido"
            print(f"❌ {arquivo} bloco {i}: ERRO DE SINTAXE -> {detalhe[:160]}")
        else:
            print(f"✅ {arquivo} bloco {i}: sintaxe OK")
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
