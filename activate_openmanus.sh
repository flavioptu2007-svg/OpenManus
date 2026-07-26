#!/bin/bash
# Ativa o OpenManus sem o PYTHONPATH do Python 3.14 do sistema
unset PYTHONPATH
source "$(dirname "$0")/.venv/bin/activate"
echo "✅ OpenManus ativado! Ambiente: Python $(python --version)"
echo "   PYTHONPATH limpo (sem interferência do sistema 3.14)"
