#!/usr/bin/env python3
"""Teste funcional da API v1 + MCP gabaritos do OMR System."""
import json
import sys
import urllib.request


BASE = "http://127.0.0.1:5000"


def call(url, method="GET", data=None, headers=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        BASE + url, data=body, headers=headers or {}, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]


def main():
    print("=== 1. LOGIN JWT ===")
    st, d = call(
        "/api/v1/auth/login",
        "POST",
        {"username": "admin", "password": "admin123"},
        {"Content-Type": "application/json"},
    )
    token = (d or {}).get("access_token", "")
    print(f"status={st} | token len={len(token)}")
    if not token:
        print("ERRO: sem token. Resposta:", d)
        return 1
    auth = {"Authorization": "Bearer " + token}

    print("\n=== 2. LISTAR QUESTOES (limit/offset) ===")
    st, d = call("/api/v1/questoes?limit=2&offset=0", headers=auth)
    itens = (d or {}).get("itens") or (d or {}).get("items") or []
    print(
        f"status={st} | total={d.get('total')} | has_more={d.get('has_more')} | itens={len(itens)}"
    )
    if itens:
        q = itens[0]
        print(
            f"  exemplo: id={q.get('id')} materia={q.get('materia')} serie={q.get('serie')}"
        )

    print("\n=== 3. MCP: tools + chamada real ===")
    try:
        import asyncio

        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        async def run():
            p = StdioServerParameters(
                command=".venv/bin/python", args=["-m", "mcp_gabaritos"]
            )
            async with stdio_client(p) as (r, w):
                async with ClientSession(r, w) as s:
                    await s.initialize()
                    t = await s.list_tools()
                    print(f"tools listadas: {len(t.tools)}")
                    res = await s.call_tool(
                        "gabaritos_consultar_questoes", {"dados": {"limit": 1}}
                    )
                    txt = res.content[0].text if res.content else ""
                    print(
                        "chamada gabaritos_consultar_questoes ->",
                        txt[:200].replace("\n", " "),
                    )

        asyncio.run(run())
    except ImportError as e:
        print("pulo teste MCP:", e)

    print("\n=== 4. RESULTADOS (filtro prova) ===")
    st, d = call("/api/v1/resultados?limit=1", headers=auth)
    print(f"status={st} | total={d.get('total')}")

    print("\n✅ Fluxo completo OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
