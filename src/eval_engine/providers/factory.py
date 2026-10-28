"""Builds real providers from config + environment. Imports SDKs lazily."""

import os
import sqlite3

from eval_engine.config import AppConfig, ConfigError
from eval_engine.prompts import PromptRegistry
from eval_engine.providers.base import Provider
from eval_engine.providers.client import LLMClient, ProviderFactory
from eval_engine.storage.calls import CallLog, ResponseCache, UsageCounter


def _api_key(config: AppConfig, provider: str) -> str:
    env = config.providers[provider].api_key_env
    if env is None:
        raise ConfigError(f"provider {provider!r} has no api_key_env configured")
    key = os.environ.get(env, "").strip()
    if not key:
        raise ConfigError(f"{env} is not set; add it to .env (see .env.example)")
    return key


def make_provider_factory(config: AppConfig) -> ProviderFactory:
    def factory(name: str) -> Provider:
        if name == "gemini":
            from eval_engine.providers.gemini import GeminiProvider

            return GeminiProvider(_api_key(config, name))
        if name == "mistral":
            from eval_engine.providers.mistral import MistralProvider

            return MistralProvider(_api_key(config, name))
        if name == "groq":
            from eval_engine.providers.groq_cloud import GroqProvider

            return GroqProvider(_api_key(config, name))
        if name == "ollama":
            from eval_engine.providers.ollama_local import OllamaProvider

            return OllamaProvider(os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
        raise ConfigError(f"no adapter for provider {name!r}")

    return factory


def build_client(
    config: AppConfig,
    conn: sqlite3.Connection,
    prompts: PromptRegistry | None = None,
    *,
    use_cache: bool = True,
) -> LLMClient:
    return LLMClient(
        config,
        prompts or PromptRegistry(),
        make_provider_factory(config),
        cache=ResponseCache(conn),
        call_log=CallLog(conn),
        usage=UsageCounter(conn),
        use_cache=use_cache,
    )
