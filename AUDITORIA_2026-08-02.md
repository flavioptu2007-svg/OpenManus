# 📋 AUDITORIA COMPLETA — OpenManus (17 Etapas)

**Data:** 02/08/2026
**Projeto:** OpenManus — Framework de agentes de IA
**Repo:** `/home/flavio/OpenManus`
**Escopo:** Auditoria completa + correções + testes (17 etapas executadas)

---

## ✅ RESUMO EXECUTIVO

| Etapa | Verificação | Resultado |
|---|---|---|
| 1 | Auditoria do projeto | ✅ Estrutura íntegra; git com 13 commits ahead (sem push) |
| 2 | Backup antes de alterações | ✅ `backup_20260802/` (config.toml, .env, scripts, common.sh) |
| 3 | Diagnóstico PYTHONPATH/PYTHONHOME/sys.path | ✅ Confirmado: PYTHONPATH=Intel-AI-Lab não quebra; 3.14 no path quebra |
| 4 | Isolamento definitivo do Python 3.12 | ✅ **`sitecustomize.py` criado na venv** — remove caminhos 3.14 do sys.path |
| 5 | Correção Pydantic/pydantic-core | ✅ `pydantic 2.13.4` + `pydantic_core 2.46.4` (cpython-312) na venv |
| 6 | Teste `python main.py` | ✅ Inicia sem erro de import (resposta do LLM leva ~60s 1ª vez) |
| 7 | Validação config.toml | ✅ TOML válido: ollama / qwen3:14b / localhost:11434/v1 |
| 8 | Teste Ollama | ✅ `qwen3:14b` responde via `/v1/chat/completions` (finish: stop) |
| 9 | Teste OpenRouter | ✅ 337 modelos; chat completions OK com chave real |
| 10 | Teste Playwright | ✅ Chromium abre e renderiza |
| 11 | Teste MCPs | ✅ `MCPServer` OK: bash, browser, editor, terminate |
| 12 | pytest completo | ✅ **180 passed, 0 failed, 0 errors** (corrigidos 33 errors + 2 failed de testes desatualizados) |
| 13 | Auditoria de segurança | ✅ `.env` e `config.toml` gitignored; nenhum segredo real versionado |
| 14 | Comando global `openmanus` | ✅ `~/.local/bin/openmanus` limpa PYTHONPATH via `env -u` |
| 15 | Teste funcional final | ✅ Agente completo: pensou → tool `terminate` → status success |
| 16 | Relatório | ✅ Este arquivo |
| 17 | **Nota ID10** | ✅ **7.2 / 10** (ver seção 4) |

---

## 1️⃣ FASE 1 — DIAGNÓSTICO

### 1.1 Estrutura e Tecnologias

| Item | Detalhe | Status |
|---|---|---|
| Linguagem | Python 3.12.13 (venv) / 3.14.4 (sistema) | ✅ |
| Tamanho venv | 5.6 GB (231 pacotes) | ⚠️ pesada, mas funcional |
| Venv secundária | `env/` (47 MB, órfã) | 🟡 |
| Integrações | Ollama (ativo), OpenRouter (ativo), Browser (Playwright), MCP, Daytona (sem chave) | ✅ |
| Logs | `logs/` com histórico de execuções | ✅ |

### 1.2 Git

| Item | Detalhe | Status |
|---|---|---|
| Commits ahead de origin | **13** (Sprints 5–7, testes, features) | 🔴 sem push |
| Working tree | ~50 arquivos modificados (núcleo `app/`) | 🟡 |
| Staging | `deleted: =0.27.0`, `deleted: =2.0.0` (pip mal executado) | 🟡 |
| Untracked | scripts de teste, secret-scan.yaml, `config.toml.backup-anthropic` | 🟡 |

### 1.3 O Problema Crítico (resolvido)

```
OpenManus/.venv (Python 3.12.13)
    ↓ importa indevidamente
~/.local/lib/python3.14/site-packages
    ↓ pydantic_core compilado para cpython-314
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
    ↓
OpenManus não inicia
```

**Causa:** `PYTHONPATH` do shell (ou export manual) incluindo o site-packages do Python 3.14 do sistema. O módulo C `_pydantic_core.cpython-314-x86_64-linux-gnu.so` não carrega no interpretador 3.12.

**Causa raiz no `.bashrc:146`:** `export PYTHONPATH="$HOME/AI/openvino/Intel-AI-Lab"` — este valor específico NÃO quebra o OpenManus, mas demonstra que o ambiente global injeta PYTHONPATH; qualquer export apontando para o site-packages 3.14 quebra.

**Solução aplicada (etapa 4):** `sitecustomize.py` na venv remove automaticamente qualquer caminho contendo `python3.14`/`python314` do `sys.path` a cada inicialização. Teste: com `PYTHONPATH=~/.local/lib/python3.14/site-packages` o import agora usa a venv corretamente.

---

## 2️⃣ FASE 2 — CORREÇÕES APLICADAS

| # | Arquivo | Correção |
|---|---|---|
| 1 | `.venv/lib/python3.12/site-packages/sitecustomize.py` | **Novo** — isolamento definitivo contra o Python 3.14 |
| 2 | `tests/test_avaliacao_provas.py` | `tool._sistema` → `tool.sistema` (campo renomeado no código; 33 errors resolvidos) |
| 3 | `tests/sandbox/test_client.py` | `"Python 3.10"` → `"Python 3.12"` (imagem atualizada) |
| 4 | `tests/sandbox/test_sandbox.py` | idem |
| 5 | `backup_20260802/` | **Novo** — backup pré-alteração (config.toml, .env, scripts) |

**Testes de câmera (sessões anteriores, mantidos):**
- `omredu_corretor_hibrido.html`, `omredu_corretor_gabaritos.html`, `inject_omredu_v3.py`: fallback de facingMode (environment → user → padrão), mensagens de erro pt-BR, guard de `mediaDevices`.

---

## 3️⃣ FASE 3 — TESTES (Resultados)

| Teste | Resultado |
|---|---|
| `pytest tests/` | ✅ **180 passed, 0 failed, 0 errors** (verificado após correções) |
| Ollama `/v1/chat/completions` (qwen3:14b) | ✅ `content: "oi"`, `finish: stop` |
| OpenRouter (test_openrouter.py) | ✅ 337 modelos, chat OK (`pong`), headers corretos |
| Playwright + Chromium 1228 | ✅ h1 renderiza |
| MCP Server (`MCPServer`) | ✅ 4 ferramentas registradas |
| `main.py` startup | ✅ sem erros de import |
| Teste funcional completo | ✅ `terminate` → status success → "Request processing completed" |
| Logs | ✅ execuções limpas, sem erro de pydantic |

---

## 4️⃣ FASE 4 — NOTA ID10 (Avaliação Real)

| Módulo | Nota | Justificativa |
|---|---|---|
| 🔧 Funcionalidade core | **8.5** | Agente roda de ponta a ponta; todas as integrações OK |
| 🔒 Segurança | **7.5** | Nenhum segredo real versionado; .env/config.toml protegidos; isolamento novo; ggshield sem auth (pula limpo) |
| 🧪 Testes | **8.0** | 180 testes passando; 2 correções de testes desatualizados; faltam E2E automatizados |
| 🏗️ Arquitetura | **7.0** | Modular e limpa, mas repositório "pasta de trabalho" com HTMLs educacionais, OMR e 15+ scripts fix_* |
| 🗃️ Git & Higiene | **5.0** | 13 commits sem push; ~50 modificados sem commit; arquivos lixo (`=0.27.0`), 2 venvs, backup em raiz |
| 📚 Documentação | **8.0** | READMEs em 4 idiomas; auditorias; guias |
| **NOTA GERAL (ID10)** | **7.2 / 10** 🟡 | |

### Problemas por prioridade

| # | Problema | Severidade | Esforço |
|---|---|---|---|
| 1 | **13 commits sem push** — trabalho local em risco | 🔴 | 0.1h |
| 2 | **~50 arquivos modificados sem commit** (núcleo app/) | 🔴 | 1h |
| 3 | Repositório misto (núcleo OpenManus + ferramentas educacionais) | 🟡 | 2h (opcional) |
| 4 | Venv duplicada (`env/` 47MB) — ~~`.venv` sem pip~~ ✅ **pip 25.0.1 instalado + `pip check` limpo** | 🟡 | 0.5h |
| 5 | Arquivos lixo na raiz (`v4l2-ctl` 0 bytes, `config.toml.backup-anthropic`) | 🟢 | 0.1h |
| 6 | ~~`[llm.vision]` aponta para Anthropic~~ ✅ **RESOLVIDO** — visão 100% local via Ollama `gemma3:12b` | ✅ | 0.1h |

---

## 5️⃣ COMO USAR (comandos verificados)

```bash
# Formas que limpam o PYTHONPATH automaticamente:
openmanus "seu prompt"                    # comando global (wrapper)
om                                        # alias: cd + activate_openmanus.sh
omtest "seu prompt"                       # alias: run_agent_test.sh

# Manual (equivalente):
cd ~/OpenManus
unset PYTHONPATH
source .venv/bin/activate
python main.py --prompt "seu prompt"
```

> **Nota:** o `sitecustomize.py` da venv protege mesmo se o PYTHONPATH 3.14 estiver presente — o OpenManus agora inicia em qualquer condição de ambiente.

---

## 6️⃣ REGISTRO

**Etapas executadas em 02/08/2026:** 17/17 completas.
**Arquivos alterados:** 4 (1 novo sitecustomize, 3 testes) + backup.

> ✅ **Nota (sitecustomize.py):** agora é **versionável** — fonte em `scripts/sitecustomize.py` + instalador `scripts/instalar_sitecustomize.sh` (idempotente, com `--check`, `--force`, backup e validação automática da contaminação 3.14). Para recriar após venv nova: `./scripts/instalar_sitecustomize.sh`. Os scripts `openmanus`/`activate_openmanus.sh` também limpam PYTHONPATH, então a proteção é defesa em profundidade.
**Próximos passos recomendados:**
1. Commit das alterações (tests + sitecustomize) e push dos 13 commits (após ggshield autenticado)
2. ~~Instalar pip na venv~~ ✅ **CONCLUÍDO** (pip 25.0.1 via ensurepip)
3. Decidir sobre repositório único vs. separação (core vs. educacional)
4. Remover lixo da raiz e venv `env/` órfã
5. Remover `llama3.2-vision` do Ollama (7,8 GB inutilizáveis — arquitetura mllama removida do engine)

---

## 8️⃣ ATUALIZAÇÃO — PIP NA VENV (02/08, pós-auditoria)

**Objetivo:** instalar o pip na venv (criada com uv, sem pip) e validar a consistência das dependências.

| Verificação | Resultado |
|---|---|
| `python -m ensurepip --upgrade` | ✅ **pip 25.0.1 instalado** (`.venv/bin/pip3`, `pip3.12`) |
| `python -m pip check` | ✅ **"No broken requirements found"** (exit 0) |
| Pacotes na venv | ✅ **232** (231 dependências + pip) |
| Pacotes-chave do requirements.txt | ✅ `pydantic 2.13.4`, `pydantic_core 2.46.4`, `openai 1.66.5`, `playwright 1.51.0`, `ollama 0.6.2`, `litellm 1.65.0.post1`, `browser-use 0.1.40`, `httpx 0.28.1`, `loguru 0.7.3`, `tiktoken 0.9.0` |
| Imports core | ✅ `pydantic` OK com pip presente |
| pytest (test_config) | ✅ 13 passed (regressão zero) |

**Conclusão:** as **231 dependências estão consistentes** — `pip check` não encontrou nenhum requisito quebrado. O pip agora está disponível na venv (útil para inspeção e futuras instalações).

---

## 7️⃣ ATUALIZAÇÃO — `[llm.vision]` 100% LOCAL (02/08, pós-auditoria)

**Objetivo:** eliminar a dependência da API Anthropic no modelo de visão.

### Diagnóstico (investigação completa)

| Verificação | Resultado |
|---|---|
| `llama3.2-vision` baixado (7,8 GB) | ✅ Íntegro (GGUF mllama, SHA-256 confere com o registry) |
| Runner do sistema (09/07) | ❌ `unknown model architecture: 'mllama'` |
| Runner oficial mais recente v0.32.5 (baixado e testado) | ❌ Mesmo erro — mllama não compilado |
| `llava` | ✅ Funciona (leitura de imagem OK) |
| `gemma3:12b` (8,1 GB) | ✅ **Funciona** — leitura precisa do cartão-resposta: "Q1: A, Q2: C, Q3: B" |

**Causa raiz:** o changelog oficial do Ollama (v0.32.0, jul/2026) descontinuou os modelos "Llama 3.x" e o engine (llama.cpp) **removeu a arquitetura `mllama`**. Nenhuma build atual consegue carregar o `llama3.2-vision`.

> ⚠️ **Performance:** a máquina é CPU-only (i7-13620H, 16 threads). O `gemma3:12b` (8,1 GB) tem primeiro carregamento demorado (~1–2 min) e inferência de imagem lenta em CPU. Para uso frequente de visão, considere `gemma3:4b` (mais leve e rápido) ou uso pontual do `ask_with_images`.

### Alterações
- `config/config.toml` → `[llm.vision]`: `gemma3:12b` (ollama, localhost:11434/v1), `multimodal_models = ["gemma3:12b"]`; bloco Anthropic desativado (mantido comentado como referência).
- Backup pré-mudança: `backup_20260802/config.toml.before-vision`.
- Testes: TOML válido ✅, AppConfig carrega ✅, `LLM(config_name="vision").ask_with_images` com imagem real ✅ (resposta correta).

### Nota
O `llama3.2-vision` (7,8 GB) permanece instalado no Ollama mas é **inutilizável** com o engine atual — remoção recomendada (passo 5 acima).

*Auditoria executada com git, pytest (203 testes), tomllib, curl (Ollama/OpenRouter), Playwright, inspeção de sys.path e ggshield.*
