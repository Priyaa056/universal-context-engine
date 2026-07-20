import os
from dotenv import load_dotenv

from context.models import FormattedContext
from .llm_providers import BaseLLMProvider, GroqProvider


class ResponseService:
    def __init__(self, provider: BaseLLMProvider = None):
        load_dotenv()

        if provider is None:
            try:
                from config import get_settings
                provider_name = get_settings().LLM_PROVIDER
            except ImportError:
                provider_name = os.getenv("LLM_PROVIDER", "groq")

            provider_name = (provider_name or "groq").lower()
            if provider_name == "groq":
                provider = GroqProvider()
            else:
                raise ValueError(f"Unknown LLM provider: {provider_name}")

        self.provider = provider

    def generate(self, context: FormattedContext) -> str:
        if context is None:
            raise ValueError("Formatted context cannot be None")

        prompt = self._build_prompt(context)

        try:
            return self.provider.generate(prompt)
        except Exception as exc:
            print(exc)

            if context.context_text.strip():
                return (
                    "LLM unavailable.\n\n"
                    + context.context_text[:2000]
                )

            return "No relevant information found."

    def _build_prompt(self, context: FormattedContext) -> str:
        return f"""
Answer ONLY using the uploaded document context.

If the answer is not present, say:

"I don't know based on the uploaded documents."

Question:
{context.question}

Context:
{context.context_text}
"""