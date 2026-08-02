#!/bin/bash
# Instala scripts/sitecustomize.py na venv do OpenManus (cópia ativa).
#
# POR QUÊ: o sitecustomize.py remove do sys.path qualquer diretório do
# Python 3.14 do sistema (ex.: ~/.local/lib/python3.14/site-packages), que
# quebraria o import de pydantic_core na venv 3.12 com:
#     ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
#
# A cópia ativa (.venv/.../site-packages/sitecustomize.py) vive fora do git.
# Este script recria a partir da fonte versionada scripts/sitecustomize.py,
# tornando o isolamento reprodutível após recriar a venv (ex.: uv venv).
#
# Uso:
#   ./scripts/instalar_sitecustomize.sh          # instala e valida
#   ./scripts/instalar_sitecustomize.sh --check  # só verifica (não altera)
#   ./scripts/instalar_sitecustomize.sh --force  # sobrescreve mesmo se igual
#
# Saída: 0 = ok, 1 = falha.
set -euo pipefail

# ── Convenção do projeto (lib/common.sh) ──────────────────────────────────────
# Resolve a RAIZ do projeto a partir do diretório deste script (scripts/).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# common.sh fica em lib/ (na raiz). Carregamos só as funções de diagnóstico;
# este script não ativa a venv (a instalação é feita via `python` da própria
# venv, sem necessidade de ativar PYTHONPATH limpo — o sitecustomize é o
# mecanismo de proteção e não deve depender do shell).
if [ -f "$PROJECT_ROOT/lib/common.sh" ]; then
    # shellcheck source=lib/common.sh
    source "$PROJECT_ROOT/lib/common.sh"
fi

SOURCE_FILE="$SCRIPT_DIR/sitecustomize.py"
CHECK_ONLY=0
FORCE=0

while [ $# -gt 0 ]; do
    case "$1" in
        --check) CHECK_ONLY=1 ;;
        --force) FORCE=1 ;;
        *) echo "Uso: $0 [--check|--force]" >&2; exit 2 ;;
    esac
    shift
done

# ── Validar precondições ──────────────────────────────────────────────────────
if [ ! -f "$SOURCE_FILE" ]; then
    echo "❌ Fonte não encontrada: $SOURCE_FILE" >&2
    exit 1
fi
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "❌ .venv não encontrado em $PROJECT_ROOT" >&2
    echo "   Crie primeiro: uv venv --python 3.12 && uv pip install -r requirements.txt" >&2
    exit 1
fi

VENV_PY="$PROJECT_ROOT/.venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
    echo "❌ Python da venv não encontrado: $VENV_PY" >&2
    exit 1
fi

# Descobre o site-packages da venv de forma robusta (3.12, mas funciona para
# qualquer versão — o projeto usa 3.12).
SITE_PACKAGES="$("$VENV_PY" -c 'import site; print(site.getsitepackages()[0])' 2>/dev/null || true)"
if [ -z "$SITE_PACKAGES" ] || [ ! -d "$SITE_PACKAGES" ]; then
    echo "❌ Não foi possível localizar site-packages da venv" >&2
    exit 1
fi

TARGET="$SITE_PACKAGES/sitecustomize.py"
VENV_PY_VERSION="$("$VENV_PY" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

echo "📁 Projeto:    $PROJECT_ROOT"
echo "🐍 Python venv: $VENV_PY_VERSION ($VENV_PY)"
echo "📦 site-packages: $SITE_PACKAGES"
echo "🎯 Alvo:       $TARGET"
echo ""

# ── Modo --check: só verificar ────────────────────────────────────────────────
if [ "$CHECK_ONLY" = "1" ]; then
    if [ -f "$TARGET" ]; then
        if cmp -s "$SOURCE_FILE" "$TARGET"; then
            echo "✅ sitecustomize.py já instalado e idêntico à fonte."
            exit 0
        else
            echo "⚠️  sitecustomize.py instalado, mas DIFERENTE da fonte:"
            echo "   fonte: $SOURCE_FILE"
            echo "   ativo: $TARGET"
            echo "   Rode sem --check para atualizar (ou --force)."
            exit 2
        fi
    else
        echo "⚠️  sitecustomize.py NÃO instalado na venv."
        echo "   Rode sem --check para instalar."
        exit 2
    fi
fi

# ── Instalar ──────────────────────────────────────────────────────────────────
NEEDS_INSTALL=1
if [ -f "$TARGET" ] && cmp -s "$SOURCE_FILE" "$TARGET"; then
    NEEDS_INSTALL=0
    echo "ℹ️  sitecustomize.py já idêntico à fonte."
fi

if [ "$NEEDS_INSTALL" = "1" ] || [ "$FORCE" = "1" ]; then
    # Backup da cópia ativa (se houver e for diferente) antes de sobrescrever
    if [ -f "$TARGET" ] && ! cmp -s "$SOURCE_FILE" "$TARGET"; then
        BACKUP="$TARGET.bak.$(date +%Y%m%d%H%M%S)"
        cp "$TARGET" "$BACKUP"
        echo "💾 Backup da cópia anterior: $BACKUP"
    fi
    cp "$SOURCE_FILE" "$TARGET"
    echo "✅ Instalado: $TARGET"
fi

# ── Validar (só quando não for --check) ───────────────────────────────────────
echo ""
echo "🧪 Validando import com PYTHONPATH contaminado (3.14)..."

# Simula o cenário que quebrava: PYTHONPATH apontando para o site-packages 3.14
if [ -d "$HOME/.local/lib/python3.14/site-packages" ]; then
    # Aviso (RuntimeWarning) é esperado — o que importa é o pydantic_core vir da venv
    OUTPUT="$(PYTHONPATH="$HOME/.local/lib/python3.14/site-packages" "$VENV_PY" -c '
import pydantic_core, sys
expected = "site-packages" in pydantic_core.__file__ and "python3.14" not in pydantic_core.__file__
print(f"pydantic_core: {pydantic_core.__file__}")
print("OK_VENV" if expected else "ERRO_FORA_DA_VENV")
' 2>&1)"
    echo "$OUTPUT" | grep -v 'RuntimeWarning\|warnings.warn\|sitecustomize(OpenManus)'
    RESULT="$(echo "$OUTPUT" | grep -o 'OK_VENV\|ERRO_FORA_DA_VENV' | head -1)"
    if [ "$RESULT" = "OK_VENV" ]; then
        echo "✅ Validação OK: pydantic_core importado da venv mesmo com PYTHONPATH 3.14."
        exit 0
    else
        echo "❌ Validação FALHOU: pydantic_core veio de fora da venv." >&2
        exit 1
    fi
else
    echo "ℹ️  site-packages do 3.14 não presente no sistema — validação de contaminação pulada."
    echo "   (Import normal:)"
    "$VENV_PY" -c 'import pydantic_core; print("OK:", pydantic_core.__file__)'
    exit 0
fi
