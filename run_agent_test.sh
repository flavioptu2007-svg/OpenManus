#!/bin/bash
# Roda o OpenManus (main.py) com um prompt de teste.
# Uso:
#   ./run_agent_test.sh                          # usa o prompt padrão
#   ./run_agent_test.sh "sua tarefa aqui"        # usa um prompt customizado
#   OPENMANUS_PROMPT="..." ./run_agent_test.sh   # ou via env var (preferencial)
#   PROMPT="..." ./run_agent_test.sh             # ou via env var (fallback)
#   ./run_agent_test.sh --flow                    # + suíte de validação completa (test_om_flow.sh)
#   CHECK_FLOW=1 ./run_agent_test.sh              # idem, via env var
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

# Flag opcional --flow: roda também o test_om_flow.sh (suíte de validação
# completa: aliases om/omtest, venv limpo, início do agente + status de auth).
# Alternativa via env var: CHECK_FLOW=1.
CHECK_FLOW="${CHECK_FLOW:-0}"
if [ "${1:-}" = "--flow" ]; then
    CHECK_FLOW=1
    shift
fi

# Prompt de teste: primeiro argumento > OPENMANUS_PROMPT > PROMPT > padrão
# OPENMANUS_PROMPT é o env var preferencial (nome não-genérico); PROMPT é o fallback
PROMPT="${1:-${OPENMANUS_PROMPT:-${PROMPT:-Quem foi Leonardo da Vinci? Responda em 3 frases.}}}"

echo "🤖 OpenManus — teste do agente via $(python --version)"
echo "   PYTHONPATH limpo | venv ativado"
echo "   Prompt: \"$PROMPT\""
echo ""

# Roda o agente (passo principal)
if [ "$CHECK_FLOW" = "1" ]; then
    # Em modo --flow, capturamos o exit do agente para NÃO abortar antes de
    # rodar a suíte de validação (o set -e não pode matar o fluxo aqui).
    set +e
    ./.venv/bin/python main.py --prompt "$PROMPT"
    AGENT_EXIT=$?
    echo ""
    echo "🧪 Suíte de validação completa (test_om_flow.sh)..."
    "$SCRIPT_DIR/test_om_flow.sh"
    FLOW_EXIT=$?
    set -e
    echo ""
    if [ "$AGENT_EXIT" -ne 0 ]; then
        echo "⚠️  Agente falhou (exit $AGENT_EXIT) — veja o traceback acima."
        echo "    A suíte de fluxo ainda foi executada (exit $FLOW_EXIT)."
    fi
    # Exit não-zero se QUALQUER passo falhou (agente OU suíte)
    [ "$AGENT_EXIT" -eq 0 ] && [ "$FLOW_EXIT" -eq 0 ]
else
    ./.venv/bin/python main.py --prompt "$PROMPT"
fi
