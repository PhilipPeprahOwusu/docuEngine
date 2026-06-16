"""Google Gemini Provider"""
from app.llm.base_provider import BaseLLMProvider
from typing import Any


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider"""

    def get_default_model(self) -> str:
        return "gemini-pro"

    def get_available_models(self) -> list:
        return [
            "gemini-pro",
            "gemini-pro-vision"
        ]

    def invoke(self, prompt: str, **kwargs) -> Any:
        """
        Invoke Google Gemini API.

        Returns object with .content attribute for compatibility.
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")

        genai.configure(api_key=self.api_key)

        # Override defaults with kwargs
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        model_name = kwargs.get("model", self.model)

        model = genai.GenerativeModel(model_name)

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        # Create response object with .content attribute for compatibility
        class Response:
            def __init__(self, content):
                self.content = content

        return Response(response.text)
