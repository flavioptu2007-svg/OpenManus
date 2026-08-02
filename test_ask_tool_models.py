#!/usr/bin/env python3
"""Testa o ask_tool com o payload REAL do agente (coleção de ferramentas do Manus).

Uso:
    ./.venv/bin/python test_ask_tool_models.py
"""

import asyncio
import sys

from dotenv import load_dotenv


load_dotenv()

from app.config import LLMSettings, config  # noqa: E402
from app.llm import LLM  # noqa: E402
from app.prompt.manus import SYSTEM_PROMPT  # noqa: E402
from app.schema import Message, ToolChoice  # noqa: E402
from app.tool import Terminate, ToolCollection  # noqa: E402
from app.tool.ask_human import AskHuman  # noqa: E402
from app.tool.avaliacao_provas import AvaliacaoProvas  # noqa: E402
from app.tool.browser_use_tool import BrowserUseTool  # noqa: E402
from app.tool.python_execute import PythonExecute  # noqa: E402
from app.tool.str_replace_editor import StrReplaceEditor  # noqa: E402


CANDIDATES = [
    "inclusionai/ling-3.0-flash:free",
    "cohere/north-mini-code:free",
    "google/gemma-4-26b-a4b-it:free",
    # gpt-oss-20b:free REMOVIDO — rejeita os tool schemas do Manus com 422
    # (dependency/property-name assertions). Mantido apenas em comentário.
]


REAL_TOOLS = ToolCollection(
    PythonExecute(),
    BrowserUseTool(),
    StrReplaceEditor(),
    AskHuman(),
    AvaliacaoProvas(),
    Terminate(),
).to_params()

REAL_SYSTEM_PROMPT = [
    Message.system_message(SYSTEM_PROMPT.format(directory=config.workspace_root))
]


async def test_one(model: str, base: LLMSettings) -> tuple[str, str]:
    cfg = LLMSettings(**{**base.model_dump(), "model": model})
    llm = LLM(model, {"default": cfg})
    try:
        msg = await llm.ask_tool(
            [Message.user_message("Responda apenas: OK")],
            system_msgs=REAL_SYSTEM_PROMPT,
            tools=REAL_TOOLS,
            tool_choice=ToolChoice.AUTO,
            timeout=60,
        )
        if msg is None:
            return model, "OK (resposta vazia)"
        content = (msg.content or "")[:40]
        calls = len(getattr(msg, "tool_calls", None) or [])
        return model, f"OK content={content!r} tool_calls={calls}"
    except Exception as exc:  # noqa: BLE001
        return model, f"FAIL {type(exc).__name__}: {str(exc)[:130]}"


async def main() -> int:
    base = config.llm["default"]
    results = await asyncio.gather(*(test_one(m, base) for m in CANDIDATES))
    for model, res in results:
        print(f"-- {model}")
        print(f"   {res}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
