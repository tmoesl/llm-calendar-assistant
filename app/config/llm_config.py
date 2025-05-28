"""
LLM Configuration Module

Configuration for LLM providers using Pydantic Settings and Field validation.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderSettings(BaseSettings):
    """Base settings for LLM providers."""

    temperature: float = Field(default=0.0, description="Randomness for generation.")
    max_tokens: int = Field(default=2048, description="Max tokens per completion.")
    max_retries: int = Field(default=3, description="Retries on API failure.")
    timeout: int = Field(default=30, description="API request timeout (seconds).")

    # Configure .env loading for all subclasses
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class OpenAISettings(LLMProviderSettings):
    """Settings for OpenAI."""

    api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    default_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    @field_validator("api_key", mode="before")
    @classmethod
    def validate_api_key(cls, value: str) -> str:
        """Validate the OpenAI API key."""
        if not value.startswith("sk-"):
            raise ValueError("OpenAI API key must start with sk-")
        return value


class AnthropicSettings(LLMProviderSettings):
    """Settings for Anthropic."""

    api_key: str = Field(..., validation_alias="ANTHROPIC_API_KEY")
    default_model: str = "claude-3-5-sonnet-20240620"

    @field_validator("api_key", mode="before")
    @classmethod
    def validate_api_key(cls, value: str) -> str:
        """Validate the Anthropic API key."""
        if not value.startswith("cla-"):
            raise ValueError("Anthropic API key must start with cla-")
        return value


class LLMConfig(BaseSettings):
    """Configuration for all LLM providers."""

    # Note: Use default_factory to defer instantiation until LLMConfig is created
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
