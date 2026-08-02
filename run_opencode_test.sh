#!/bin/bash
# Roda o OpenCode (opencode run) com um prompt de teste.
# Uso:
#   ./run_opencode_test.sh                                # prompt + modelo padrão (free)
#   ./run_opencode_test.sh "sua tarefa aqui"              # prompt customizado
#   OPENMANUS_PROMPT="..." ./run_opencode_test.sh         # ou via env var
#   ./run_opencode_test.sh "tarefa" "openrouter/openai/gpt-4o-mini"  # modelo customizado
#   MODEL="..." ./run_opencode_test.sh                    # ou modelo via env var
set -euo pipefail

# Resolve o diretório do script de forma robusta (funciona mesmo com caminho
# relativo, PATH ou symlink), ao contrário de $(dirname "$0") frágil.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
cd "$SCRIPT_DIR"

# Limpa o PYTHONPATH do Python 3.14 do sistema (mesmo padrão do activate_openmanus.sh)
om_unset_pythonpath

# Localiza o binário do opencode (PATH padrão + ~/.opencode/bin + ~/.local/bin)
export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"
if ! command -v opencode >/dev/null 2>&1; then
    echo "❌ opencode não encontrado. Instale com:" >&2
    echo "   curl -fsSL https://opencode.ai/install | bash" >&2
    exit 1
fi

# Prompt: 1º argumento > OPENMANUS_PROMPT > PROMPT > padrão
PROMPT="${1:-${OPENMANUS_PROMPT:-${PROMPT:-Diga apenas a palavra OK}}}"
# Modelo: 2º argumento > MODEL > padrão (gratuito, não exige chave OpenRouter)
MODEL="${2:-${MODEL:-opencode/deepseek-v4-flash-free}}"

echo "🤖 OpenCode test — $(opencode --version 2>&1 | head -1)"
echo "   PYTHONPATH limpo"
echo "   Model:  $MODEL"
echo "   Prompt: \"$PROMPT\""
echo ""

# opencode run abre o TUI interativo se stdin for um terminal (trava em scripts);
# por isso o prompt é enviado via pipe (modo não-interativo).
echo "$PROMPT" | opencode run --model "$MODEL" "$PROMPT"
