"""Isolamento da venv OpenManus contra o Python 3.14 do sistema.

A venv usa CPython 3.12. Se o PYTHONPATH do shell (ou um export manual)
incluir ~/.local/lib/python3.14/site-packages, o interpretador 3.12 tenta
importar pacotes compilados para 3.14 (ex.: pydantic_core._pydantic_core
compilado como cpython-314), o que quebra o OpenManus com:
    ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'

Este sitecustomize é carregado automaticamente a cada inicialização do
Python desta venv e remove do sys.path qualquer diretório do Python 3.14,
garantindo que todos os imports venham da própria venv (3.12).

⚠️  Este arquivo é a FONTE VERSIONADA. A cópia ativa fica em:
    .venv/lib/python3.12/site-packages/sitecustomize.py
    (fora do git — recrie com scripts/instalar_sitecustomize.sh)
"""

import sys
import warnings


_314_MARKERS = ("python3.14", "python314")

_removed = []
for _p in list(sys.path):
    if not isinstance(_p, str):
        continue
    if any(m in _p for m in _314_MARKERS):
        try:
            sys.path.remove(_p)
            _removed.append(_p)
        except ValueError:
            pass

if _removed:
    warnings.warn(
        "sitecustomize(OpenManus): removidos do sys.path os diretórios do "
        "Python 3.14 do sistema (incompatíveis com esta venv 3.12):\n  "
        + "\n  ".join(_removed),
        RuntimeWarning,
    )
