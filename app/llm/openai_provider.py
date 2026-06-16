"""OpenAI (ChatGPT) Provider"""
from app.llm.base_provider import BaseLLMProvider
from typing import Any


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider (GPT-4, GPT-3.5-turbo, etc.)"""

    def get_default_model(self) -> str:
        return "gpt-4-turbo-preview"

    def get_available_models(self) -> list:
        return [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]

    def invoke(self, prompt: str, **kwargs) -> Any:
        """
        Invoke OpenAI API.

        Returns object with .content attribute for compatibility.
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

        client = OpenAI(api_key=self.api_key)

        # Override defaults with kwargs
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        model = kwargs.get("model", self.model)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Create response object with .content attribute for compatibility
        class Response:
            def __init__(self, content):
                self.content = content

        return Response(response.choices[0].message.content)
