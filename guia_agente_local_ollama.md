# Como Montar um Agente de Ações Local (Passo a Passo)

A forma mais comum e poderosa hoje é unir um LLM local (o "cérebro") a funções Python (as "mãos"),
usando o mecanismo nativo de **function calling** do Ollama — não apenas gerando texto,
mas fazendo o modelo escolher e executar ferramentas reais.

## Passo 1: Instalar o Servidor de IA Local

Instale o [Ollama](https://ollama.com/), que permite rodar modelos de linguagem direto na
sua máquina sem enviar dados para a nuvem.

1. Baixe e instale o Ollama para seu sistema operacional.
2. Baixe um modelo leve e adequado para automação (o `qwen2.5:7b` tem bom suporte a tool calling):

```bash
ollama pull qwen2.5:7b
```

> Use `pull`, não `run` — `run` abre um chat interativo no terminal; `pull` só baixa o modelo,
> que será chamado depois via API/Python.

3. Confirme que o serviço está rodando:

```bash
ollama list
```

## Passo 2: Criar as Ferramentas de Execução (Python)

Crie funções Python que a IA poderá invocar. Cada função deve ser previsível, ter escopo
limitado e validar suas próprias entradas — o modelo não deve ter acesso irrestrito ao sistema.

```python
import os
import platform
import subprocess

# Diretório-base permitido — nenhuma operação de arquivo sai daqui
BASE_DIR = os.path.expanduser("~/Desktop")

def abrir_programa(nome_app: str) -> str:
    """Abre um aplicativo instalado no sistema operacional."""
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
    """Cria uma pasta dentro do diretório permitido (BASE_DIR)."""
    caminho = os.path.join(BASE_DIR, nome_pasta)
    # Impede que o modelo tente sair do diretório permitido (ex: "../../etc")
    if not os.path.abspath(caminho).startswith(os.path.abspath(BASE_DIR)):
        return "Operação bloqueada: caminho fora do diretório permitido."
    os.makedirs(caminho, exist_ok=True)
    return f"Pasta criada em: {caminho}"

def listar_arquivos(nome_pasta: str = "") -> str:
    """Lista os arquivos de uma subpasta dentro do diretório permitido."""
    caminho = os.path.join(BASE_DIR, nome_pasta)
    if not os.path.abspath(caminho).startswith(os.path.abspath(BASE_DIR)):
        return "Operação bloqueada: caminho fora do diretório permitido."
    if not os.path.isdir(caminho):
        return f"Pasta não encontrada: {caminho}"
    return "\n".join(os.listdir(caminho)) or "(pasta vazia)"
```

**Por que isso importa:** cada função retorna uma string de status (não silenciosa),
valida caminhos contra um diretório-base e trata exceções — sem isso, um erro de execução
derruba o agente inteiro, ou pior, ele executa fora do escopo pretendido.

### Ferramenta 4 — Calculadora Segura (sem `eval()`!)

Use `ast.NodeVisitor` para avaliar expressões matemáticas sem expor o sistema a injeção
de código. O modelo pode calcular, mas nunca executar `exec()`, `os.system()` ou acessar
variáveis.

```python
import ast
import operator

# Operadores permitidos — qualquer outro é bloqueado
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
    """Avalia expressão matemática sem eval() arbitrário."""
    tree = ast.parse(expr, mode="eval")

    def _visitar(node):
        if isinstance(node, ast.Expression):
            return _visitar(node.body)
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Constante não numérica: {node.value}")
        elif isinstance(node, (ast.UnaryOp, ast.BinOp)):
            op = _OPERADORES.get(type(node.op))
            if not op:
                raise ValueError(f"Operador não permitido")
            args = [_visitar(node.operand)] if isinstance(node, ast.UnaryOp) else [_visitar(node.left), _visitar(node.right)]
            return op(*args)
        else:
            raise ValueError(f"Expressão inválida: {type(node).__name__}")

    return _visitar(tree)

def calcular(expressao: str) -> str:
    """Calcula expressão matemática de forma segura.
    Suporta: +, -, *, /, //, %, **, parênteses.
    Bloqueia: chamadas de função, variáveis, imports."""
    try:
        resultado = _eval_seguro(expressao)
        if isinstance(resultado, float) and resultado == int(resultado):
            resultado = int(resultado)
        return f"{expressao} = {resultado}"
    except Exception as e:
        return f"Erro: {e}"
```

**Diferencial de segurança:** `_eval_seguro` percorre a árvore sintática (AST) e só permite
nós de constantes numéricas e operadores aritméticos — qualquer tentativa de chamar funções,
aceder a variáveis ou executar código é bloqueada na raiz.

### Ferramenta 5 — Clima (gratuito, sem API Key)

Consulte a previsão do tempo usando o serviço público [wttr.in](https://wttr.in) — sem
necessidade de chave de API, sem cadastro.

```python
import urllib.parse
import urllib.request

def consultar_clima(cidade: str = "Paracatu", formato: str = "compacto") -> str:
    """Previsão do tempo via wttr.in (gratuito, sem API key)."""
    try:
        # URL-encoding suporta acentos: Brasília, São Paulo...
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
        return f"Erro: {e}"
```

**Diferencial:** usa `urllib.parse.quote()` para codificar acentos — "Brasília", "São Paulo"
e "Rio de Janeiro" funcionam sem erro de encoding.

### Ferramenta 6 — Git (Whitelist de Comandos)

Disponibilize operações Git ao modelo com uma whitelist rigorosa — o modelo só pode
invocar os comandos pré-aprovados, nunca `git push`, `git reset --hard` ou comandos
arbitrários.

```python
import subprocess

# Whitelist: comandos que o modelo PODE executar
COMANDOS_GIT_PERMITIDOS = {
    "status": ["git", "status", "--short"],
    "log": ["git", "log", "--oneline", "-10"],
    "branch": ["git", "branch", "-a"],
    "diff": ["git", "diff", "--stat"],
}

PROJETO_DIR = os.path.expanduser("~/OpenManus")

def _executar_git(comando: list[str]) -> str:
    """Executa comando Git no diretório do projeto com timeout."""
    try:
        resultado = subprocess.run(
            comando, cwd=PROJETO_DIR,
            capture_output=True, text=True, timeout=15,
        )
        if resultado.returncode != 0:
            return f"Erro Git: {resultado.stderr.strip()[:300]}"
        return resultado.stdout.strip() or "(sem saída)"
    except subprocess.TimeoutExpired:
        return "Erro: comando Git excedeu o tempo limite (15s)"
    except FileNotFoundError:
        return "Erro: Git não encontrado. Instale com 'sudo apt install git'"
    except Exception as e:
        return f"Erro: {e}"

def git_status() -> str:
    """Status do repositório (arquivos modificados, staged)."""
    return _executar_git(COMANDOS_GIT_PERMITIDOS["status"])

def git_log(limite: int = 10) -> str:
    """Histórico de commits recentes (máx 30)."""
    n = min(max(1, limite), 30)
    return _executar_git(["git", "log", "--oneline", f"-{n}"])

def git_branch() -> str:
    """Lista branches do repositório."""
    return _executar_git(COMANDOS_GIT_PERMITIDOS["branch"])

def git_add_commit(mensagem: str) -> str:
    """⚠️ AÇÃO DESTRUTIVA: faz git add -A e git commit.
    Requer confirmação humana explícita — nunca executar automaticamente."""
    add = subprocess.run(["git", "add", "-A"], cwd=PROJETO_DIR,
                         capture_output=True, text=True, timeout=15)
    if add.returncode != 0:
        return f"Erro no add: {add.stderr.strip()[:300]}"
    commit = subprocess.run(["git", "commit", "-m", mensagem], cwd=PROJETO_DIR,
                            capture_output=True, text=True, timeout=15)
    if commit.returncode != 0:
        if "nothing to commit" in commit.stderr:
            return "Nada para commitar."
        return f"Erro no commit: {commit.stderr.strip()[:300]}"
    return f"✅ Commit realizado!\n{commit.stdout.strip()}"
```

**Diferencial de segurança:** `COMANDOS_GIT_PERMITIDOS` é um dicionário fixo — o modelo
não pode inventar comandos. `git_add_commit` é marcada como destrutiva e sempre passa pelo
passo de confirmação humana.

## Passo 3: Conectar a IA às Ferramentas (Function Calling Real)

Aqui está o ponto que normalmente quebra em tutoriais: **declarar as ferramentas em JSON Schema**
e deixar o modelo decidir qual chamar — e então **de fato executar** a função escolhida,
em vez de só imprimir o texto de resposta.

> 💡 O `agente_ollama.py` na raiz do projeto já implementa **todas as 10 ferramentas**
> com o executor completo. Basta rodar `python3 agente_ollama.py`.

O Ollama aceita as funções Python diretamente (com docstring e type hints), sem
precisar escrever JSON Schema manualmente. Basta passar a lista de funções:

```python
import ollama

# Lista de ferramentas disponíveis para o modelo
# O Ollama infere o JSON Schema automaticamente das docstrings e type hints!
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

def executar_agente(pedido_usuario: str):
    print(f"\n🧠 Modelo: qwen3")
    print(f"📝 Pedido: {pedido_usuario}\n")

    messages = [{"role": "user", "content": pedido_usuario}]

    # Primeira chamada — modelo decide se precisa de ferramenta
    response = ollama.chat(
        model="qwen3",
        messages=messages,
        tools=FERRAMENTAS,  # <-- passa as funções Python diretamente!
    )

    messages.append(response["message"])
    tool_calls = response["message"].get("tool_calls", [])

    if not tool_calls:
        print("💬 Resposta:", response["message"]["content"])
        return

    # Executa cada ferramenta solicitada
    for chamada in tool_calls:
        nome = chamada["function"]["name"]
        args = chamada["function"]["arguments"]

        print(f"🔧 Modelo quer executar: {nome}({args})")

        # ---- Confirmação humana (obrigatório para ações destrutivas) ----
        confirmar = input("  Permitir? (Enter=s, n=N): ").strip().lower()
        if confirmar == "n":
            print("  ⛔ Ação cancelada pelo usuário.")
            continue
        # -----------------------------------------------------------------

        # Mapeia nome → função
        funcao = {f.__name__: f for f in FERRAMENTAS}.get(nome)
        if not funcao:
            print(f"  ⚠️ Função desconhecida: {nome}")
            continue

        try:
            resultado = funcao(**args)
            print(f"  ✅ Resultado: {str(resultado)[:200]}...")
        except Exception as e:
            resultado = f"Erro: {e}"
            print(f"  ❌ Erro: {e}")

        # Envia resultado de volta pro modelo para resposta contextualizada
        messages.append({
            "role": "tool",
            "name": nome,
            "content": str(resultado),
        })

    # Resposta final do modelo após executar as ferramentas
    final = ollama.chat(model="qwen3", messages=messages)
    print(f"\n💬 Resposta final:\n{final['message']['content']}")


if __name__ == "__main__":
    executar_agente("Qual a previsão do tempo em Brasília e o status do Git?")
```

**Novidade importante:** diferente da versão manual com JSON Schema, o código acima
passa as **funções Python diretamente** para `ollama.chat(tools=FERRAMENTAS)` — o Ollama
infere o JSON Schema automaticamente a partir das docstrings e type hints.

Agora o ciclo é completo: **modelo decide → Python confirma e executa → resultado real**.
Isso é o que diferencia um agente de ações de um chatbot comum.

Para automações mais complexas (múltiplos passos encadeados, memória de longo prazo,
múltiplos agentes especializados), frameworks como **LangChain** ou **CrewAI** ajudam a
organizar esse fluxo — mas o núcleo é sempre este: schema de ferramentas + execução
condicionada + confirmação.

## Passo 4: Checklist de Segurança (obrigatório, não opcional)

Permitir que uma IA execute comandos locais é equivalente a dar acesso de automação a um
script que você não escreveu linha a linha. Antes de rodar em produção:

- **Whitelist de ações**: só exponha ao modelo as funções que ele realmente precisa —
  nunca `exec()`, `eval()` ou `subprocess` genérico sem filtro de comando.
- **Confirmação humana** para qualquer ação destrutiva ou irreversível (deletar,
  sobrescrever, enviar dados).
- **Escopo de diretório**: restrinja leitura/escrita a uma pasta específica (como no
  exemplo acima), nunca à raiz do sistema.
- **Ambiente isolado**: rode o agente em um `venv` dedicado, idealmente com o usuário do
  sistema operacional com permissões limitadas (não como administrador/root).
- **Log de auditoria**: registre toda chamada de função com timestamp, argumentos e
  resultado — essencial para depurar e para saber o que o agente já fez.
- **Timeout em comandos**: qualquer `subprocess` deve ter `timeout=` definido para evitar
  travamentos.

## Requisitos de Hardware Recomendados

Para rodar modelos capazes de entender comandos e executar function calling com boa velocidade:

| Porte do modelo | RAM mínima | GPU recomendada | Uso típico |
|---|---|---|---|
| 3B–7B (ex: qwen2.5:7b, llama3.2:3b) | 8–16 GB | 6 GB+ VRAM ou Apple Silicon M1+ | Automação leve, respostas rápidas |
| 8B–14B (ex: qwen3:14b) | 16–32 GB | 8–12 GB+ VRAM | Melhor raciocínio para tarefas encadeadas |
| 30B+ | 32 GB+ | 24 GB+ VRAM (ou CPU/offload) | Agentes com múltiplas etapas complexas |

Processador Quad-Core ou superior em qualquer faixa. Modelos quantizados (ex: Q4_K_M)
reduzem os requisitos de RAM/VRAM com perda de qualidade geralmente aceitável para automação.

---

## Tabela Resumo — 10 Ferramentas do Agente Local

| # | Ferramenta | Descrição | Segurança | Categoria |
|---|---|---|---|---|
| 1 | `criar_pasta` | Cria pastas no `~/Desktop` | ✅ Path traversal protected | Sistema de Arquivos |
| 2 | `abrir_programa` | Abre aplicativos instalados | ✅ `try/except` + fallback SO | Sistema |
| 3 | `listar_arquivos` | Lista conteúdo de diretórios | ✅ Restrito ao Desktop | Sistema de Arquivos |
| 4 | `ler_arquivo` | Lê conteúdo de arquivos texto | ✅ Path traversal protected | Sistema de Arquivos |
| 5 | `calcular` | Expressões matemáticas | ✅ **AST seguro** (sem `eval()`!) | Utilitário |
| 6 | `consultar_clima` | Previsão do tempo via wttr.in | ✅ Sem API key, timeout 10s | Utilitário |
| 7 | `git_status` | Status do repositório | ✅ Whitelist de comandos | Git |
| 8 | `git_log` | Histórico de commits | ✅ Whitelist, timeout 15s | Git |
| 9 | `git_branch` | Lista branches | ✅ Whitelist | Git |
| 10 | `git_add_commit` | Add + commit | ⚠️ **Destrutiva**: requer confirmação humana | Git |

### Exemplos de Uso Rápido

```bash
# Modo interativo (com confirmação)
python3 agente_ollama.py

# Testar ferramentas individualmente (útil para debugging)
python3 -c "from agente_ollama import calcular; print(calcular('2**10 + 5*3'))"
python3 -c "from agente_ollama import consultar_clima; print(consultar_clima('Brasília'))"
python3 -c "from agente_ollama import git_status; print(git_status())"
```

---

## Relação com o OpenManus

O guia acima descreve o padrão **exato** que o OpenManus implementa, mas em escala
industrial. Comparação:

| Conceito no Guia | Implementação no OpenManus |
|---|---|
| `ollama.chat(tools=...)` | `LLM.ask_tool(tools=...)` em `app/llm.py` |
| `ferramentas_schema` (JSON Schema) | `BaseTool.to_param()` em `app/tool/base.py` |
| `FERRAMENTAS_DISPONIVEIS` (dict) | `ToolCollection` + `tool_map` em `app/tool/tool_collection.py` |
| `for chamada in tool_calls:` | `ToolCallAgent.act()` em `app/agent/toolcall.py` |
| Confirmação humana | `AskHuman` tool em `app/tool/ask_human.py` |
| `BASE_DIR` (path restriction) | `_safe_resolve_path()` + `clean_path()` no sandbox |
| Blocklist de comandos | `_check_blocked_commands()` em `app/tool/bash.py` |
| Log de auditoria | `MetricsCollector` em `app/utils/metrics.py` |
| Timeout em subprocess | `asyncio.wait_for(proc.communicate(), timeout)` em `python_execute.py` |
| Rate limiting | `RateLimiter` em `app/llm.py` |
| Planejamento multi-passo | `PlanningFlow` em `app/flow/planning.py` |
| Cache de busca | `SearchCache` em `app/tool/web_search.py` |
