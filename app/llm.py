import os
from typing import Protocol

from google import genai


class LLMClient(Protocol):
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        ...


class GeminiLLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.7-flash",
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = self.client.interactions.create(
            model=self.model,
            system_instruction=system_prompt,
            input=user_prompt,
        )

        return response.output_text