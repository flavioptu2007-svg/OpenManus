#!/usr/bin/env python3
"""Agente Local com Ollama — Teste de Function Calling.

Baseado no guia em guia_agente_local_ollama.md.
Usa qwen3 (ou qwen2.5) para executar ferramentas locais com segurança.

Ferramentas:
  • Arquivos: criar_pasta, listar_arquivos, ler_arquivo
  • Sistema: abrir_programa
  • Calculadora: calcular (matemática segura)
  • Clima: consultar_clima (wttr.in, sem API key)
  • Git: git_status, git_log, git_branch, git_add_commit (whitelist)
"""

import ast
import operator
import os
import platform
import subprocess
import sys
import urllib.parse
import urllib.request

import ollama

# ─── Configuração ─────────────────────────────────────────────
MODELO = "qwen3"  # ou "qwen2.5" se preferir
BASE_DIR = os.path.expanduser("~/Desktop")
PROJETO_DIR = os.path.expanduser("~/OpenManus")  # Diretório do projeto Git


# ══════════════════════════════════════════════════════════════
# FERRAMENTA 1 — CALCULADORA SEGURA
# ══════════════════════════════════════════════════════════════

# Operadores permitidos para eval seguro
_OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_seguro(expr: str) -> float:
    """Avalia expressão matemática de forma segura (sem exec/eval arbitrário)."""
    tree = ast.parse(expr, mode="eval")

    def _visitar(node):
        if isinstance(node, ast.Expression):
            return _visitar(node.body)
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Constante não numérica: {node.value}")
        elif isinstance(node, ast.UnaryOp):
            op = _OPERADORES.get(type(node.op))
            if not op:
                raise ValueError(f"Operador não permitido: {type(node.op).__name__}")
            return op(_visitar(node.operand))
        elif isinstance(node, ast.BinOp):
            op = _OPERADORES.get(type(node.op))
            if not op:
                raise ValueError(f"Operador não permitido: {type(node.op).__name__}")
            return op(_visitar(node.left), _visitar(node.right))
        else:
            raise ValueError(f"Expressão inválida: {type(node).__name__}")

    return _visitar(tree)


def calcular(expressao: str) -> str:
    """Calcula uma expressão matemática de forma segura.

    Suporta: +, -, *, /, //, %, **, parênteses e números decimais.
    NÃO suporta: chamadas de função, variáveis, imports.

    Args:
        expressao: Expressão matemática (ex: "2 + 3 * 4", "(10 + 5) / 3", "2 ** 10").

    Returns:
        Resultado da operação.

    Examples:
        calcular("2 + 2") -> "2 + 2 = 4"
        calcular("(15 + 5) * 2") -> "(15 + 5) * 2 = 40.0"
    """
    try:
        resultado = _eval_seguro(expressao)
        # Formata inteiros sem .0
        if isinstance(resultado, float) and resultado == int(resultado):
            resultado = int(resultado)
        return f"{expressao} = {resultado}"
    except Exception as e:
        return f"Erro ao calcular '{expressao}': {e}"


# ══════════════════════════════════════════════════════════════
# FERRAMENTA 2 — CLIMA (wttr.in)
# ══════════════════════════════════════════════════════════════

def consultar_clima(cidade: str = "Paracatu", formato: str = "compacto") -> str:
    """Consulta a previsão do tempo atual para uma cidade via wttr.in (gratuito, sem API key).

    Args:
        cidade: Nome da cidade (ex: "Paracatu", "Brasília", "São Paulo").
        formato: Formato da resposta ("completo" ou "compacto").

    Returns:
        Previsão do tempo formatada.
    """
    try:
        # wttr.in retorna texto simples
        if formato == "compacto":
            url = f"https://wttr.in/{urllib.parse.quote(cidade)}?format=%C+%t+%w+%h"
        else:
            url = f"https://wttr.in/{urllib.parse.quote(cidade)}?0&lang=pt"

        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            dados = resp.read().decode("utf-8").strip()

        if formato == "compacto":
            return f"☁️ Clima em {cidade}: {dados}"
        return f"☁️ Clima em {cidade}:\n{dados}"
    except Exception as e:
        return f"Erro ao consultar clima de '{cidade}': {e}"


# ══════════════════════════════════════════════════════════════
# FERRAMENTA 3 — GIT (Whitelist de Comandos)
# ══════════════════════════════════════════════════════════════

# Comandos Git permitidos (whitelist rigorosa)
COMANDOS_GIT_PERMITIDOS = {
    "status": ["git", "status", "--short"],
    "log": ["git", "log", "--oneline", "-10"],
    "branch": ["git", "branch", "-a"],
    "diff": ["git", "diff", "--stat"],
}


def _executar_git(comando: list[str]) -> str:
    """Executa comando Git no diretório do projeto com timeout."""
    try:
        resultado = subprocess.run(
            comando,
            cwd=PROJETO_DIR,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if resultado.returncode != 0:
            erro = resultado.stderr.strip()[:300]
            return f"Erro Git: {erro}"
        saida = resultado.stdout.strip()
        return saida if saida else "(sem saída)"
    except subprocess.TimeoutExpired:
        return "Erro: comando Git excedeu o tempo limite (15s)"
    except FileNotFoundError:
        return "Erro: Git não encontrado. Instale com 'sudo apt install git'"
    except Exception as e:
        return f"Erro ao executar Git: {e}"


def git_status() -> str:
    """Mostra o status atual do repositório Git (arquivos modificados, staged, etc.).

    Returns:
        Status formatado do repositório.
    """
    return _executar_git(COMANDOS_GIT_PERMITIDOS["status"])


def git_log(limite: int = 10) -> str:
    """Mostra o histórico de commits recentes.

    Args:
        limite: Número de commits a mostrar (máx 30).

    Returns:
        Log formatado dos commits.
    """
    n = min(max(1, limite), 30)
    return _executar_git(["git", "log", "--oneline", f"-{n}"])


def git_branch() -> str:
    """Lista as branches do repositório, destacando a atual.

    Returns:
        Lista de branches.
    """
    return _executar_git(COMANDOS_GIT_PERMITIDOS["branch"])


def git_add_commit(mensagem: str) -> str:
    """Faz git add -A e git commit com a mensagem fornecida.

    ⚠️ AÇÃO DESTRUTIVA: requer confirmação humana explícita.

    Args:
        mensagem: Mensagem descritiva do commit.

    Returns:
        Resultado do commit.
    """
    # Add
    add_result = subprocess.run(
        ["git", "add", "-A"],
        cwd=PROJETO_DIR,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if add_result.returncode != 0:
        return f"Erro no git add: {add_result.stderr.strip()[:300]}"

    # Commit
    commit_result = subprocess.run(
        ["git", "commit", "-m", mensagem],
        cwd=PROJETO_DIR,
        capture_output=True,
        text=True,
        timeout=15,
    )
    saida = commit_result.stdout.strip()
    if commit_result.returncode != 0:
        erro = commit_result.stderr.strip()
        if "nothing to commit" in erro:
            return "Nada para commitar. Todos os arquivos já estão atualizados."
        return f"Erro no commit: {erro[:300]}"
    return f"✅ Commit realizado!\n{saida}"


# ══════════════════════════════════════════════════════════════
# FERRAMENTAS EXISTENTES
# ══════════════════════════════════════════════════════════════

def abrir_programa(nome_app: str) -> str:
    """Abre um aplicativo instalado no sistema operacional.

    Args:
        nome_app: Nome do aplicativo a abrir (ex: 'Firefox', 'Code').

    Returns:
        Mensagem de status da operação.
    """
    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.startfile(nome_app)
        elif sistema == "Darwin":  # macOS
            subprocess.run(["open", "-a", nome_app], check=True)
        else:  # Linux
            subprocess.run(["xdg-open", nome_app], check=True)
        return f"'{nome_app}' aberto com sucesso."
    except Exception as e:
        return f"Erro ao abrir '{nome_app}': {e}"


def criar_pasta(nome_pasta: str) -> str:
    """Cria uma pasta dentro do diretório permitido (Desktop).

    Args:
        nome_pasta: Nome da pasta a ser criada.

    Returns:
        Mensagem de status da operação.
    """
    caminho = os.path.join(BASE_DIR, nome_pasta)
    if not os.path.abspath(caminho).startswith(os.path.abspath(BASE_DIR)):
        return "Operação bloqueada: caminho fora do diretório permitido."
    os.makedirs(caminho, exist_ok=True)
    return f"Pasta criada em: {caminho}"


def listar_arquivos(nome_pasta: str = "") -> str:
    """Lista os arquivos de uma subpasta dentro do diretório permitido.

    Args:
        nome_pasta: Subpasta a listar (opcional). Se vazio, lista a raiz.

    Returns:
        Lista de arquivos/pastas ou mensagem de erro.
    """
    caminho = os.path.join(BASE_DIR, nome_pasta)
    if not os.path.abspath(caminho).startswith(os.path.abspath(BASE_DIR)):
        return "Operação bloqueada: caminho fora do diretório permitido."
    if not os.path.isdir(caminho):
        return f"Pasta não encontrada: {caminho}"
    conteudo = os.listdir(caminho)
    return "\n".join(conteudo) if conteudo else "(pasta vazia)"


def ler_arquivo(nome_arquivo: str, pasta: str = "") -> str:
    """Lê o conteúdo de um arquivo texto dentro do diretório permitido.

    Args:
        nome_arquivo: Nome do arquivo a ler.
        pasta: Subpasta opcional onde o arquivo está.

    Returns:
        Conteúdo do arquivo ou mensagem de erro.
    """
    caminho = os.path.join(BASE_DIR, pasta, nome_arquivo)
    if not os.path.abspath(caminho).startswith(os.path.abspath(BASE_DIR)):
        return "Operação bloqueada: caminho fora do diretório permitido."
    if not os.path.isfile(caminho):
        return f"Arquivo não encontrado: {caminho}"
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"


# Lista de ferramentas disponíveis para o modelo
FERRAMENTAS = [
    criar_pasta,
    abrir_programa,
    listar_arquivos,
    ler_arquivo,
    calcular,
    consultar_clima,
    git_status,
    git_log,
    git_branch,
    git_add_commit,
]


# ─── Executor do Agente ───────────────────────────────────────
def executar_agente(pedido_usuario: str):
    """Executa o ciclo completo: modelo decide → confirmação → execução."""
    print(f"\n🧠 Modelo: {MODELO}")
    print(f"📝 Pedido: {pedido_usuario}\n")

    messages = [{"role": "user", "content": pedido_usuario}]

    # Primeira chamada — modelo decide se precisa de ferramenta
    response = ollama.chat(
        model=MODELO,
        messages=messages,
        tools=FERRAMENTAS,
    )

    messages.append(response["message"])
    tool_calls = response["message"].get("tool_calls", [])

    if not tool_calls:
        # Modelo respondeu só com texto
        print("💬 Resposta:", response["message"]["content"])
        return

    # Executa cada ferramenta solicitada
    for chamada in tool_calls:
        nome = chamada["function"]["name"]
        args = chamada["function"]["arguments"]

        print(f"🔧 Modelo quer executar: {nome}({args})")

        # Confirmação humana
        confirmar = input("  Permitir? (Enter=s, n=N): ").strip().lower()
        if confirmar == "n":
            print("  ⛔ Ação cancelada pelo usuário.")
            continue

        # Mapeia nome → função
        funcao = {f.__name__: f for f in FERRAMENTAS}.get(nome)
        if not funcao:
            print(f"  ⚠️ Função desconhecida: {nome}")
            continue

        try:
            resultado = funcao(**args)
            print(f"  ✅ Resultado: {resultado[:200]}{'...' if len(resultado) > 200 else ''}")
        except Exception as e:
            resultado = f"Erro: {e}"
            print(f"  ❌ Erro: {e}")

        # Envia resultado de volta pro modelo
        messages.append({
            "role": "tool",
            "name": nome,
            "content": str(resultado),
        })

    # Resposta final do modelo após executar as ferramentas
    final = ollama.chat(model=MODELO, messages=messages)
    print(f"\n💬 Resposta final:\n{final['message']['content']}")


# ─── Main ─────────────────────────────────────────────────────
if __name__ == "__main__":
    # Pega pedido da linha de comando ou pergunta
    pedido = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not pedido:
        pedido = input("📌 Digite seu pedido: ").strip()
    if not pedido:
        pedido = "Crie uma pasta chamada TesteAgente no Desktop e liste os arquivos de lá."

    executar_agente(pedido)
