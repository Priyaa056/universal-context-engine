import os
from dotenv import load_dotenv
from google import genai

from context.models import FormattedContext


class ResponseService:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        load_dotenv()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is missing")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, context: FormattedContext) -> str:
        if context is None:
            raise ValueError("Formatted context cannot be None")

        prompt = self._build_prompt(context)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text or "No response generated."

        except Exception as e:
            return (
                "AI response generation is temporarily unavailable.\n\n"
                "Retrieved Context:\n\n"
                f"{context.context_text[:1000]}\n\n"
                f"Reason: {str(e)[:300]}"
            )

    def _build_prompt(self, context: FormattedContext) -> str:
        return f"""
You are Universal Context Engine.

Answer the user's question using ONLY the uploaded document context.

If the answer is not present in the context, say:
"I don't know based on the uploaded documents."

Question:
{context.question}

Context:
{context.context_text}
"""