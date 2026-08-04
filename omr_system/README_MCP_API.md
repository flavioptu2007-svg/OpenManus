# Sistema de Gabaritos — API v1 + Servidor MCP (`gabaritos_mcp`)

Este documento cobre as duas peças novas do sistema OMR:

1. **API v1** — endpoints REST adicionais (`/api/v1/gabaritos/processar`,
   `/api/v1/resultados`) + paginação `limit`/`offset` nas listagens existentes.
2. **`gabaritos_mcp`** — servidor [MCP](https://modelcontextprotocol.io)
   (FastMCP, transporte **stdio**) que expõe o sistema como 7 tools para
   agentes de IA.

> Autenticação: **X-API-Key** (header `X-API-Key`) **ou JWT** (login
> `admin` / `admin123`). A API key é lida da variável de ambiente
> `GABARITOS_API_KEY` — nunca fica em código.

---

## 1. Instalação (uma vez)

```bash
cd omr_system
unset PYTHONPATH            # evita contaminação por site-packages de outro Python

# Ambiente isolado (Python 3.12) + dependências da API
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt

# Dependências do MCP (fastmcp, httpx, pydantic)
uv pip install --python .venv/bin/python -r mcp_gabaritos/requirements-mcp.txt
```

## 2. Variáveis de ambiente

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `GABARITOS_API_KEY` | se usar X-API-Key | — | Chave validada no header `X-API-Key` |
| `GABARITOS_API_URL` | não | `http://127.0.0.1:5000` | Base URL da API (usada pelo MCP) |
| `PORT` | não | `5000` | Porta do servidor Flask |

Exemplo:

```bash
export GABARITOS_API_KEY="chave-secreta-local-123"
```

## 3. Subir a API

```bash
cd omr_system
unset PYTHONPATH
./.venv/bin/python run.py          # porta 5000 (ou PORT=5055 ./.venv/bin/python run.py)
```

Na inicialização, colunas `materia`/`serie` são adicionadas à tabela `questoes`
de forma idempotente (não destrói dados existentes).

### Teste rápido com curl

```bash
# Login (JWT)
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

# Listar questões com filtro e paginação limit/offset (JWT)
curl -s "http://127.0.0.1:5000/api/v1/questoes?materia=História&limit=2&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Processar gabarito por base64 (X-API-Key)
IMG=$(base64 -w0 gabarito.png)
curl -s -X POST http://127.0.0.1:5000/api/v1/gabaritos/processar \
  -H "X-API-Key: $GABARITOS_API_KEY" -H 'Content-Type: application/json' \
  -d "{\"image_base64\":\"$IMG\",\"filename\":\"gabarito.png\"}"

# Processar gabarito por multipart (JWT ou X-API-Key)
curl -s -X POST http://127.0.0.1:5000/api/v1/gabaritos/processar \
  -H "Authorization: Bearer $TOKEN" -F "image=@gabarito.png"

# Resultados com filtro por prova
curl -s "http://127.0.0.1:5000/api/v1/resultados?prova_id=1" \
  -H "X-API-Key: $GABARITOS_API_KEY"
```

## 4. Endpoints novos (API v1)

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/gabaritos/processar` | Lê gabarito (multipart `image` ou JSON `image_base64`), valida tipo/tamanho, processa com OpenCV/pyzbar e devolve leitura estruturada. Com `prova_id`, persiste como FolhaResposta. |
| `GET` | `/api/v1/resultados` | Lista resultados (`prova_id` opcional; paginação `limit`/`offset`). |

Erros no blueprint v1 seguem o formato `{"error": {"code", "message",
"suggestion"}}`. As listagens devolvem `total`, `has_more` e `next_offset`.

> As rotas legadas (`/api/v1/provas`, `/api/v1/questoes`, `/upload`,
> `/provas/<id>`, …) continuam funcionando; agora aceitam **também**
> `X-API-Key`, `limit`/`offset` e filtros `materia`/`serie`/`dificuldade`
> (em `/questoes`) — a paginação limit/offset é suportada nas listagens
> legadas, sem duplicar rotas.

## 5. Servidor MCP

```bash
cd omr_system
export GABARITOS_API_KEY="chave-secreta-local-123"
export GABARITOS_API_URL="http://127.0.0.1:5000"
./.venv/bin/python -m mcp_gabaritos        # stdio
```

> **Importante:** o servidor nunca escreve logs em stdout (o protocolo MCP usa
> stdout). Diagnósticos vão para **stderr**.

### Tools expostas

| Tool | Descrição | Hints |
|---|---|---|
| `gabaritos_criar_prova` | Cria prova por IDs de questões | write, não destrutiva, não idempotente |
| `gabaritos_listar_provas` | Lista provas (limit/offset) | read-only |
| `gabaritos_consultar_prova` | Detalhes de uma prova | read-only |
| `gabaritos_consultar_questoes` | Busca/filtra questões | read-only |
| `gabaritos_cadastrar_questao` | Cadastra questão nova | write |
| `gabaritos_processar_gabarito` | Lê imagem (path/base64); com `prova_id` grava resultado | write, não idempotente |
| `gabaritos_consultar_resultados` | Lista resultados (filtro por prova) | read-only |

Todas aceitam `response_format` (`"json"` ou `"markdown"`, padrão
`"markdown"`). Schemas de entrada são Pydantic com descrições e exemplos.

### Testar com o MCP Inspector

```bash
cd omr_system
npx @modelcontextprotocol/inspector ./.venv/bin/python -m mcp_gabaritos
```

Abra o endereço exibido no navegador, conecte e teste as tools
interativamente.

### Teste programático (SDK oficial)

O pacote `mcp` (instalado com o fastmcp) permite chamar as tools via
`ClientSession` — veja o fluxo em `mcp/client/stdio` + `call_tool`:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(command=".venv/bin/python", args=["-m", "mcp_gabaritos"])
async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        res = await session.call_tool("gabaritos_consultar_questoes",
                                      {"dados": {"materia": "História"}})
        print(res.content[0].text)
```

## 6. Avaliação (`evaluation.xml`)

`evaluation.xml` contém 10 pares pergunta/resposta **somente leitura** que
exigem múltiplas chamadas de tools e cruzamento de dados (questões × provas ×
resultados). Cada resposta descreve o passo a passo exato e o resultado
observável esperado — use com um orquestrador de avaliação de agentes MCP.

## 7. Observações

- **Segredos**: `GABARITOS_API_KEY` só em variável de ambiente; nenhuma chave
  em código, logs ou relatórios.
- **Compatibilidade**: os endpoints legados seguem funcionando (JWT +
  `page`/`per_page`) — nada foi quebrado; apenas estendido.
- **Colunas novas**: `questoes.materia` e `questoes.serie` (migração aditiva
  idempotente na inicialização).
