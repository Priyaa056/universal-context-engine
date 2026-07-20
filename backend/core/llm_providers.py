import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from openai import OpenAI


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a text response given a prompt.

        Args:
            prompt: The input text prompt to send to the LLM.

        Returns:
            The generated text response.
        """
        pass


class GroqProvider(BaseLLMProvider):
    """Groq provider implementing BaseLLMProvider using the Groq API via OpenAI client."""

    def __init__(self, model_name: str = None):
        load_dotenv()

        # Read GROQ_API_KEY from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing")

        # Read model_name. Use the provided name, or retrieve from settings / env.
        if model_name is None:
            try:
                from config import get_settings
                model_name = get_settings().GROQ_MODEL
            except (ImportError, AttributeError):
                model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are Alex, the AI assistant for Universal Context Engine.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
