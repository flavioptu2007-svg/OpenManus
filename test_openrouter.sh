#!/bin/bash
# Roda o test_openrouter.py (valida conexão, modelos e headers da OpenRouter).
# Uso:
#   ./test_openrouter.sh                            # modelo padrão (openai/gpt-4o-mini)
#   ./test_openrouter.sh --model deepseek/deepseek-v4-flash-0731   # modelo customizado
#   ./test_openrouter.sh --help                     # ajuda do test_openrouter.py
set -euo pipefail

# Resolve o diretório do script de forma robusta (funciona mesmo com caminho
# relativo, PATH ou symlink), ao contrário de $(dirname "$0") frágil.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
cd "$SCRIPT_DIR"

# Limpa o PYTHONPATH do Python 3.14 do sistema (mesmo padrão do activate_openmanus.sh)
om_unset_pythonpath

# Ativa o venv do projeto (guard compartilhado em lib/common.sh)
om_require_venv "$SCRIPT_DIR" || exit 1
source .venv/bin/activate

# test_openrouter.py lê a chave de OPENROUTER_API_KEY / LLM_API_KEY (env vars)
# ou do .env na raiz — não do config.toml.
if [ ! -f ".env" ] && [ -z "${OPENROUTER_API_KEY:-}" ] && [ -z "${LLM_API_KEY:-}" ]; then
    echo "⚠️  Nenhuma chave encontrada (OPENROUTER_API_KEY/LLM_API_KEY ou .env)."
    echo "   Crie o .env na raiz:  echo 'OPENROUTER_API_KEY=sk-or-v1-...' > .env"
    echo ""
fi

echo "🤖 OpenRouter test — $(python --version) | PYTHONPATH limpo"
echo ""

# Repassa os argumentos (ex.: --model ...) ao test_openrouter.py
./.venv/bin/python test_openrouter.py "$@"
