import os

from dotenv import load_dotenv
from google import genai

from context.models import FormattedContext


class ResponseService:
    def __init__(self, model_name: str | None = None):
        load_dotenv()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is missing")

        self.client = genai.Client(api_key=api_key)
        self.model_name = (
            model_name
            or os.getenv("GEMINI_MODEL")
            or "gemini-2.0-flash"
        )

    def generate(self, context: FormattedContext) -> str:
        if context is None:
            raise ValueError("Formatted context cannot be None")

        prompt = self._build_prompt(context)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            if response.text:
                return response.text.strip()

            return "No response was generated."

        except Exception as exc:
            print(f"LLM generation failed: {exc}")

            retrieved_context = context.context_text.strip()

            if retrieved_context:
                return (
                    "The AI model is temporarily unavailable, but I found "
                    "relevant information in your uploaded documents:\n\n"
                    f"{retrieved_context[:2000]}"
                )

            return (
                "The AI model is temporarily unavailable, and no relevant "
                "information was found in the uploaded documents."
            )

    def _build_prompt(self, context: FormattedContext) -> str:
        return f"""
You are Alex, the assistant for Universal Context Engine.

Answer the user's question using only the supplied document context.

If the answer is not present in the context, respond exactly with:
"I don't know based on the uploaded documents."

User question:
{context.question}

Uploaded document context:
{context.context_text}
""".strip()