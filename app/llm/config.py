"""
LLM Configuration Module

Configuration for LLM providers using Pydantic Settings and Field validation.
"""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderSettings(BaseSettings):
    """Base settings for LLM providers."""

    # Configure .env loading for all subclasses
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class OpenAISettings(LLMProviderSettings):
    """Settings for OpenAI."""

    api_key: SecretStr = Field(alias="OPENAI_API_KEY")
    default_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL")
    temperature: float = Field(default=0.0, alias="OPENAI_TEMPERATURE")
    max_tokens: int = Field(default=2048, alias="OPENAI_MAX_TOKENS")
    max_retries: int = Field(default=3, alias="OPENAI_MAX_RETRIES")
    timeout: int = Field(default=30, alias="OPENAI_TIMEOUT")


class AnthropicSettings(LLMProviderSettings):
    """Settings for Anthropic."""

    api_key: SecretStr = Field(alias="ANTHROPIC_API_KEY")
    default_model: str = Field(default="claude-sonnet-4-20250514", alias="ANTHROPIC_MODEL")
    temperature: float = Field(default=0.0, alias="ANTHROPIC_TEMPERATURE")
    max_tokens: int = Field(default=2048, alias="ANTHROPIC_MAX_TOKENS")
    max_retries: int = Field(default=3, alias="ANTHROPIC_MAX_RETRIES")
    timeout: int = Field(default=30, alias="ANTHROPIC_TIMEOUT")


class LLMConfig(BaseSettings):
    """Configuration for all LLM providers."""

    # Use lambda functions to create proper zero-argument callables for default_factory
    # This satisfies the type checker while allowing Pydantic to auto-load from environment
    openai: OpenAISettings = Field(default_factory=lambda: OpenAISettings())  # type: ignore
    anthropic: AnthropicSettings = Field(default_factory=lambda: AnthropicSettings())  # type: ignore

    # LLM output processing settings
    confidence_threshold: float = Field(
        default=0.7,
        alias="LLM_CONFIDENCE_THRESHOLD",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_llm_config() -> LLMConfig:
    """Get LLM configuration instance (singleton)."""
    return LLMConfig()
