import os

from dotenv import load_dotenv
from openai import OpenAI

from context.models import FormattedContext


class ResponseService:
    def __init__(self, model_name: str = "grok-4"):
        load_dotenv()

        api_key = os.getenv("XAI_API_KEY")

        if not api_key:
            raise ValueError("XAI_API_KEY is missing")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )

        self.model_name = model_name

    def generate(self, context: FormattedContext) -> str:
        if context is None:
            raise ValueError("Formatted context cannot be None")

        prompt = self._build_prompt(context)

        try:
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