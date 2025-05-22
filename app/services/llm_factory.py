"""
LLM Factory Module

This module provides a factory class for creating and managing LLM providers.
It supports multiple providers (OpenAI and Anthropic) and handles their
initialization and configuration.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

import instructor
from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel

from app.config.settings import get_settings

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def create_completion(
        self, messages: list[dict[str, str]], response_model: type[T], **kwargs: Any
    ) -> tuple[T, Any]:
        """Get structured completion from LLM"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI provider using native structured output"""

    def __init__(self, settings):
        self.settings = settings
        self.client = instructor.from_openai(OpenAI(api_key=self.settings.api_key))

    def create_completion(
        self, messages: list[dict[str, str]], response_model: type[T], **kwargs: Any
    ) -> tuple[T, Any]:
        """Use OpenAI's native structured output"""

        # Build tuning parameters with fallback to default settings
        tuning_params = {
            "model": kwargs.get("model", self.settings.default_model),
            "temperature": kwargs.get("temperature", self.settings.temperature),
            "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
            "max_retries": kwargs.get("max_retries", self.settings.max_retries),
            "timeout": kwargs.get("timeout", self.settings.timeout),
        }

        # Create the completion
        return self.client.chat.completions.create_with_completion(
            messages=messages, response_model=response_model, **tuning_params
        )


class AnthropicProvider(LLMProvider):
    """Anthropic provider using instructor for structured output."""

    def __init__(self, settings):
        self.settings = settings
        self.client = instructor.from_anthropic(Anthropic(api_key=self.settings.api_key))

    def create_completion(
        self, messages: list[dict[str, str]], response_model: type[T], **kwargs: Any
    ) -> tuple[T, Any]:
        """Use instructor for structured output."""

        # Separate system and user messages
        sys_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        usr_msg = [m for m in messages if m["role"] != "system"]

        # Build tuning parameters with fallback to default settings
        tuning_params = {
            "model": kwargs.get("model", self.settings.default_model),
            "temperature": kwargs.get("temperature", self.settings.temperature),
            "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
            "max_retries": kwargs.get("max_retries", self.settings.max_retries),
            "timeout": kwargs.get("timeout", self.settings.timeout),
        }

        # Create the completion
        return self.client.messages.create_with_completion(
            messages=usr_msg,
            response_model=response_model,
            system=sys_msg,
            **tuning_params,
        )


class LLMFactory:
    """
    Factory class for creating and managing LLM provider instances.

    This class implements the Factory pattern to create appropriate LLM provider
    instances based on the specified provider type. It supports multiple providers
    and handles their initialization and configuration.

    Attributes:
        provider: The name of the LLM provider to use
        settings: Configuration settings for the LLM provider
        llm_provider: The initialized LLM provider instance
    """

    SUPPORTED_PROVIDERS = {"openai", "anthropic"}

    def __init__(self, provider: str):
        """Initialize the LLMService with the specified provider."""
        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        self.provider = provider
        settings = get_settings()
        self.settings = getattr(settings.llm, provider)
        self.llm_provider = self._create_provider_instance()

    def _create_provider_instance(self) -> LLMProvider:
        """Create an instance of the specified LLM provider."""
        providers = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
        }

        return providers[self.provider](self.settings)

    def create_completion(
        self,
        messages: list[dict[str, str]],
        response_model: type[T],
        **kwargs: Any,
    ) -> tuple[T, Any]:
        """
        Create a completion using the configured LLM provider.

        Args:
            messages: List of message dictionaries
            response_model: Pydantic model for response structure
            **kwargs: Additional parameters for the provider

        Returns:
            Tuple containing the parsed response model and raw completion

        Raises:
            ValueError: If provider not configured
            TypeError: If response_model not Pydantic model
        """
        if not issubclass(response_model, BaseModel):
            raise TypeError("response_model must be a Pydantic BaseModel")

        return self.llm_provider.create_completion(
            messages=messages, response_model=response_model, **kwargs
        )


# SDK - OpenAI
# client = OpenAI(api_key=api_key)
# comnpletion = client.beta.chat.completions.parse(model, messages, response_format)
# completion.choices[0].message.parse
# • Retries only at API transport level.
# • If the structured output doesn’t match the schema → fails immediately.

# Instructor - OpenAI
# client = instructor.from_openai(OpenAI(api_key=api_key))
# completion = client.chat.completions.create_with_completion(model, messages, response_model)
# • Retries both transport errors and bad structured outputs.
# • Helps guarantee valid Pydantic model output even if the LLM messes up slightly.
