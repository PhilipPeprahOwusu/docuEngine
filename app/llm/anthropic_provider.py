"""Anthropic Claude Provider"""
from app.llm.base_provider import BaseLLMProvider
from typing import Any


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""

    def get_default_model(self) -> str:
        return "claude-3-5-sonnet-20241022"

    def get_available_models(self) -> list:
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]

    def invoke(self, prompt: str, **kwargs) -> Any:
        """
        Invoke Anthropic API.

        Returns object with .content attribute for compatibility.
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        client = Anthropic(api_key=self.api_key)

        # Override defaults with kwargs
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        model = kwargs.get("model", self.model)

        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Create response object with .content attribute for compatibility
        class Response:
            def __init__(self, content):
                self.content = content

        return Response(message.content[0].text)
