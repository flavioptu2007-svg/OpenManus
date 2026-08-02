#!/usr/bin/env python3
"""Atualiza config/config.toml: modelo default/vision + api_key a partir do .env.

Nunca imprime a chave completa — apenas prefixo mascarado e tamanho.
Uso:
    python update_openrouter_config.py
"""

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
CONFIG_FILE = ROOT / "config" / "config.toml"

# Modelo free verificado funcionando com o payload real do agente (ask_tool
# com a coleção completa de ferramentas do Manus). O gpt-oss-20b:free foi
# descartado: rejeita os tool schemas com 422 (dependency/property-name
# assertions). Estes 3 passaram no teste real: ling-3.0-flash, north-mini-code,
# gemma-4-26b-a4b-it.
DEFAULT_MODEL = "cohere/north-mini-code:free"
# Modelo vision-capable free (bloco [llm.vision] precisa de multimodal)
VISION_MODEL = "google/gemma-4-26b-a4b-it:free"
OLD_MODEL = "openai/gpt-oss-20b:free"  # valor atual nas linhas 44 e 76
OLD_PLACEHOLDER = "YOUR_REAL_OPENROUTER_KEY"


def main() -> int:
    import tomllib

    env_text = ENV_FILE.read_text(encoding="utf-8")
    m = re.search(r"^OPENROUTER_API_KEY=(\S+)", env_text, re.M)
    if not m:
        print("ERRO: OPENROUTER_API_KEY não encontrada no .env")
        return 1
    key = m.group(1)

    toml = CONFIG_FILE.read_text(encoding="utf-8")

    # A linha 44 ([llm] default) e a linha 76 ([llm.vision]) têm o MESMO valor
    # antigo. Substitui a 1ª ocorrência (default) pelo DEFAULT_MODEL e, em
    # seguida, a ocorrência restante (vision) pelo VISION_MODEL (count=1).
    # Regex ancorada no início da linha (re.M) para nunca casar linhas
    # comentadas (ex.: `# model = "..."`). `\s*` tolera indentação.
    model_re = re.compile(rf'^(\s*model = )"{re.escape(OLD_MODEL)}"', re.MULTILINE)
    toml, n_default = model_re.subn(rf'\1"{DEFAULT_MODEL}"', toml, count=1)
    toml, n_vision = model_re.subn(rf'\1"{VISION_MODEL}"', toml, count=1)
    # Substitui os placeholders de api_key (linhas 46 e 78) pela chave real.
    # Deliberadamente NÃO ancorada: os DOIS placeholders devem ser trocados
    # (um por bloco). Não "consertar" para ancorar.
    toml, n_key = re.subn(
        rf'(api_key = )"{re.escape(OLD_PLACEHOLDER)}"',
        rf'\1"{key}"',
        toml,
    )

    if n_default == 0 and n_key == 0:
        print("OK: já atualizado (nada a fazer)")
        return 0

    # Segurança: garante que o arquivo continua sendo TOML válido antes de gravar
    try:
        tomllib.loads(toml)
    except tomllib.TOMLDecodeError as exc:
        print(f"ERRO: config.toml ficaria inválido após a edição ({exc})")
        return 1

    CONFIG_FILE.write_text(toml, encoding="utf-8")

    print("OK: config/config.toml atualizado")
    print(f"    modelo default: {OLD_MODEL} -> {DEFAULT_MODEL}")
    if n_vision:
        print(f"    modelo vision:  {DEFAULT_MODEL} -> {VISION_MODEL}")
    if n_key:
        print(f"    api_key: {key[:9]}... len={len(key)} (mascarado)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
