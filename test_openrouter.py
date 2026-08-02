#!/usr/bin/env python3
"""Test connection to OpenRouter (https://openrouter.ai/api/v1).

Reads the API key from OPENROUTER_API_KEY or LLM_API_KEY env var,
or from the .env file in the project root (same as app/config.py).
Performs two checks:
  1. GET  /api/v1/models           - verifies the key is valid (auth)
  2. POST /api/v1/chat/completions - verifies inference works end-to-end

Sends the OpenRouter tracking headers (HTTP-Referer / X-Title) from the
OPENROUTER_HTTP_REFERER / OPENROUTER_X_TITLE env vars, using the same
defaults as app/config.py.

Usage:
    export OPENROUTER_API_KEY=sk-or-v1-...
    python3 test_openrouter.py [--model MODEL]
"""

import argparse
import os
import sys

from dotenv import load_dotenv


load_dotenv()  # same .env loading as app/config.py

BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "google/gemma-4-31b-it:free"  # free model (no credits needed)


def get_api_key() -> str:
    """Return the OpenRouter key from env vars, or exit with a message."""
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("LLM_API_KEY")
    if not key:
        print(
            "ERROR: No API key found.\n"
            "Set it first, e.g.:\n"
            "    export OPENROUTER_API_KEY=sk-or-v1-...\n"
            "or    export LLM_API_KEY=sk-or-v1-...",
            file=sys.stderr,
        )
        sys.exit(2)
    if key.startswith("YOUR_"):
        print(
            "ERROR: The key looks like a placeholder ('YOUR_...').\n"
            "Get a real key at https://openrouter.ai/settings/keys",
            file=sys.stderr,
        )
        sys.exit(2)
    return key


def get_default_headers() -> dict:
    """Return the OpenRouter tracking headers, overridable via env vars.

    Mirrors the defaults used by LLMSettings in app/config.py.
    """
    return {
        "HTTP-Referer": os.environ.get(
            "OPENROUTER_HTTP_REFERER",
            "https://github.com/FoundationAgents/OpenManus",
        ),
        "X-Title": os.environ.get("OPENROUTER_X_TITLE", "OpenManus"),
    }


def check_models(client) -> None:
    """Call GET /api/v1/models and report total count + first few models."""
    models = client.models.list()
    ids = [m.id for m in models.data]
    print(f"  OK  - GET /api/v1/models returned {len(ids)} models")
    print(f"  Sample models: {', '.join(ids[:5])}")
    if "openai/gpt-4o-mini" not in ids:
        print("  NOTE: 'openai/gpt-4o-mini' not found in the model list.")


def check_chat(client, model: str) -> None:
    """Call POST /api/v1/chat/completions with a tiny prompt."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Reply with exactly: pong"}],
            max_tokens=16,
            temperature=0.0,
        )
    except Exception as e:
        if "max_tokens" in str(e).lower() or "temperature" in str(e).lower():
            print(
                f"  SKIP - {model} rejected max_tokens/temperature "
                f"(common for reasoning models like deepseek-reasoner).\n"
                f"       Try again with --model openai/gpt-4o-mini"
            )
            return
        raise
    content = response.choices[0].message.content or ""
    usage = response.usage
    usage_str = (
        f"prompt={usage.prompt_tokens}, completion={usage.completion_tokens}"
        if usage
        else "not reported"
    )
    print(
        f"  OK  - POST /api/v1/chat/completions ({model})\n"
        f"       reply: {content!r}\n"
        f"       usage: {usage_str}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", default=DEFAULT_MODEL, help="Model ID (default: %(default)s)"
    )
    args = parser.parse_args()

    key = get_api_key()

    # Try the same OpenAI client library used by app/llm.py.
    try:
        from openai import OpenAI
    except ImportError:
        print(
            "ERROR: openai library not installed. Run: pip install openai",
            file=sys.stderr,
        )
        sys.exit(2)

    headers = get_default_headers()
    client = OpenAI(api_key=key, base_url=BASE_URL, default_headers=headers)

    print(f"Testing OpenRouter at {BASE_URL}")
    print(f"Using model: {args.model}")
    print(
        f"Headers: HTTP-Referer={headers['HTTP-Referer']} | X-Title={headers['X-Title']}\n"
    )

    # 1. Models list (auth check)
    try:
        check_models(client)
    except Exception as e:
        print(f"FAIL - GET /api/v1/models: {type(e).__name__}: {e}")
        print("The API key is likely invalid or the account has no permissions.")
        sys.exit(1)

    # 2. Chat completion (inference check)
    try:
        check_chat(client, args.model)
    except Exception as e:
        print(
            f"FAIL - POST /api/v1/chat/completions ({args.model}): {type(e).__name__}: {e}"
        )
        print("The key works, but this model may need credits or is unavailable.")
        sys.exit(1)

    print("\nSUCCESS - OpenRouter connection is working.")


if __name__ == "__main__":
    main()
