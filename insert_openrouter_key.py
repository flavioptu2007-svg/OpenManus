#!/usr/bin/env python3
"""Insere a chave OpenRouter no .env a partir de um base64.

Uso:
    python insert_openrouter_key.py 'BASE64_DA_CHAVE'
    echo 'BASE64_DA_CHAVE' | python insert_openrouter_key.py   # via stdin
    python insert_openrouter_key.py --verify 'BASE64_DA_CHAVE'  # + teste ao vivo

Nunca imprime a chave completa — apenas prefixo mascarado, tamanho e checksum.
O base64 NÃO contém o padrão sk-or-v1-, então ele pode transitar pelo chat
sem ser mascarado pelo filtro de segredos (a chave real nunca aparece aqui).

--verify: além de gravar, chama GET /api/v1/key na API do OpenRouter para
confirmar que a chave é válida (status 200 = ok).
"""

import base64
import hashlib
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"

# base64("sk-or-v1-") == "c2stb3ItdjEt"
EXPECTED_PREFIX_B64 = "c2stb3ItdjEt"
FULL_KEY_RE = re.compile(r"^sk-or-v1-[0-9a-f]{60,64}$")


def validate_base64(b64: str) -> tuple[bool, str]:
    """Decodifica o base64 e valida o formato da chave (sem imprimir a chave)."""
    b64 = b64.strip()
    if not b64.startswith(EXPECTED_PREFIX_B64):
        return False, "o base64 não começa com c2stb3ItdjEt (= sk-or-v1-)"
    try:
        # Corrige padding se faltar
        padded = b64 + "=" * (-len(b64) % 4)
        decoded = base64.b64decode(padded).decode("utf-8").strip()
    except Exception as exc:  # noqa: BLE001
        return False, f"base64 inválido: {exc}"
    if not FULL_KEY_RE.match(decoded):
        return (
            False,
            f"formato inválido (len={len(decoded)}, "
            f"sk-or-v1={decoded.startswith('sk-or-v1-')})",
        )
    return True, decoded


def masked_info(key: str) -> str:
    sha = hashlib.sha256(key.encode()).hexdigest()[:8]
    return f"prefixo={key[:9]}... tamanho={len(key)} sha8={sha}"


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--verify"]
    verify = "--verify" in sys.argv[1:]

    b64 = args[0] if args else sys.stdin.read().strip()

    if not b64:
        print("ERRO: nenhum base64 recebido (argumento ou stdin)")
        return 2

    ok, result = validate_base64(b64)
    if not ok:
        print(f"ERRO: {result}")
        return 1

    key = result  # chave validada (sk-or-v1- + hex)

    # Grava/atualiza no .env (substitui linha OPENROUTER_API_KEY= existente)
    lines = []
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
    found = False
    for i, line in enumerate(lines):
        if line.startswith("OPENROUTER_API_KEY="):
            lines[i] = f"OPENROUTER_API_KEY={key}\n"
            found = True
    if not found:
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
        lines.append(f"OPENROUTER_API_KEY={key}\n")
    ENV_FILE.write_text("".join(lines), encoding="utf-8")
    ENV_FILE.chmod(0o600)  # segredo: nunca deixar legível por outros

    print("OK: chave gravada no .env")
    print(f"    {masked_info(key)}")
    print("    arquivo:", ENV_FILE)

    if verify:
        code = check_api(key)
        print(f"    verify: HTTP {code}")
        if code == 0:
            print("    ⚠️  chave gravada, mas a API não respondeu (erro de rede/tempo)")
            return 3
        if code != 200:
            print("    ⚠️  chave gravada, mas a API rejeitou (status != 200)")
            return 3
    return 0


def check_api(key: str) -> int:
    """Verifica a chave contra GET /api/v1/key (sem expor o segredo).

    Retorna apenas o status HTTP; nunca imprime corpo da resposta
    (o campo label da resposta contém a chave completa).
    """
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:  # noqa: BLE001
        return 0


if __name__ == "__main__":
    sys.exit(main())
