"""Tests for LLMSettings configuration loading and env-var fallbacks."""

import os
from unittest.mock import patch

import pytest

from app.config import LLMSettings


DEFAULTS = {
    "model": "openai/gpt-4o-mini",
    "base_url": "https://openrouter.ai/api/v1",
}

DEFAULT_REFERER = "https://github.com/FoundationAgents/OpenManus"
DEFAULT_TITLE = "OpenManus"


def _build_settings(toml_values=None):
    """Mimic Config._load_initial_config: pass only non-None values."""
    base = dict(DEFAULTS)
    if toml_values:
        base.update(toml_values)
    kwargs = {
        "model": base.get("model"),
        "base_url": base.get("base_url"),
        "api_key": base.get("api_key"),
        "max_tokens": base.get("max_tokens", 4096),
        "max_input_tokens": base.get("max_input_tokens"),
        "temperature": base.get("temperature", 1.0),
        "api_type": base.get("api_type", ""),
        "api_version": base.get("api_version", ""),
        "http_referer": base.get("http_referer"),
        "x_title": base.get("x_title"),
    }
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    return LLMSettings(**kwargs)


_ENV_VARS = (
    "OPENROUTER_API_KEY",
    "LLM_API_KEY",
    "OPENROUTER_HTTP_REFERER",
    "OPENROUTER_X_TITLE",
)


@pytest.fixture(autouse=True)
def _clean_env():
    """Ensure tracking-header env vars are not inherited between tests.

    Saves and restores any pre-existing values so other test modules run
    afterwards see the same environment they would have seen otherwise.
    """
    saved = {var: os.environ.get(var) for var in _ENV_VARS}
    for var in _ENV_VARS:
        os.environ.pop(var, None)
    yield
    for var, value in saved.items():
        if value is None:
            os.environ.pop(var, None)
        else:
            os.environ[var] = value


class TestTrackingHeaders:
    def test_defaults_when_absent(self):
        settings = _build_settings()
        assert settings.http_referer == DEFAULT_REFERER
        assert settings.x_title == DEFAULT_TITLE

    def test_env_var_override(self):
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_HTTP_REFERER": "https://env.example.com",
                "OPENROUTER_X_TITLE": "EnvApp",
            },
        ):
            settings = _build_settings()
        assert settings.http_referer == "https://env.example.com"
        assert settings.x_title == "EnvApp"

    def test_toml_values_override_env(self):
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_HTTP_REFERER": "https://env.example.com",
                "OPENROUTER_X_TITLE": "EnvApp",
            },
        ):
            settings = _build_settings(
                {"http_referer": "https://toml.example.com", "x_title": "TomlApp"}
            )
        assert settings.http_referer == "https://toml.example.com"
        assert settings.x_title == "TomlApp"

    def test_toml_values_without_env(self):
        settings = _build_settings(
            {"http_referer": "https://toml.example.com", "x_title": "TomlApp"}
        )
        assert settings.http_referer == "https://toml.example.com"
        assert settings.x_title == "TomlApp"


class TestApiKeyFallback:
    def test_default_empty_when_absent(self):
        settings = _build_settings()
        assert settings.api_key == ""

    def test_llm_api_key_env_var(self):
        with patch.dict(os.environ, {"LLM_API_KEY": "sk-env-test"}):
            settings = _build_settings()
        assert settings.api_key == "sk-env-test"

    def test_openrouter_api_key_env_var(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            settings = _build_settings()
        assert settings.api_key == "sk-or-v1-test"

    def test_openrouter_preferred_over_llm(self):
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "sk-or-v1-test", "LLM_API_KEY": "sk-llm-test"},
        ):
            settings = _build_settings()
        assert settings.api_key == "sk-or-v1-test"

    def test_env_api_key_wins_over_toml(self):
        # README security note: "Environment variables override config.toml
        # values". An env var key must win even when TOML has a value.
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            settings = _build_settings({"api_key": "sk-toml-test"})
        assert settings.api_key == "sk-or-v1-test"

    def test_toml_api_key_used_without_env(self):
        # No env var set: falls back to the TOML value.
        settings = _build_settings({"api_key": "sk-toml-test"})
        assert settings.api_key == "sk-toml-test"

    def test_or_key_does_not_clobber_non_openrouter_provider(self):
        # Scoping: OPENROUTER_API_KEY must NOT override a key for a
        # non-OpenRouter provider (e.g. Azure, Ollama, Bedrock).
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            settings = _build_settings(
                {
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "sk-toml-test",
                }
            )
        assert settings.api_key == "sk-toml-test"

    def test_llm_key_still_overrides_any_provider(self):
        # LLM_API_KEY is the documented generic override and applies to
        # any provider, OpenRouter or not.
        with patch.dict(os.environ, {"LLM_API_KEY": "sk-llm-test"}):
            settings = _build_settings(
                {"base_url": "https://api.openai.com/v1", "api_key": "sk-toml-test"}
            )
        assert settings.api_key == "sk-llm-test"

    def test_absent_keys_do_not_raise(self):
        # Regression: explicit None previously raised ValidationError,
        # which also defeated the env-var fallback.
        settings = _build_settings()
        assert settings.model == DEFAULTS["model"]
        assert settings.base_url == DEFAULTS["base_url"]
