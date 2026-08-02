#!/bin/bash
# Ativa o OpenManus sem o PYTHONPATH do Python 3.14 do sistema
# Resolve o diretório do script de forma robusta (funciona mesmo quando
# sourced de outro diretório), ao contrário de $(dirname "$0").
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# Guard: mensagem clara se o ativador do .venv não existir, em vez de um
# erro obscuro do source (cobre também o caso de .venv ausente).
# O script é normalmente *sourced* (alias om): `return` não encerra o shell
# do usuário. Quando executado diretamente, `return` falha e cai no `exit`.
om_require_venv "$SCRIPT_DIR" || return 1 2>/dev/null || exit 1

om_unset_pythonpath
source "$SCRIPT_DIR/.venv/bin/activate"
echo "✅ OpenManus ativado! Ambiente: $(python --version)"
echo "   PYTHONPATH limpo (sem interferência do sistema 3.14)"
