import logging
from typing import TypedDict

import httpx
from google import genai
from google.genai import errors, types

from app.config.settings import Settings
from app.prompts.qa_prompt import QA_SYSTEM_INSTRUCTION


logger = logging.getLogger(__name__)


class ConversationMessage(TypedDict, total=False):
    role: str
    content: str
    include_in_history: bool


class GeminiServiceError(RuntimeError):
    """Raised when Gemini cannot provide a usable answer."""


def _history_contents(messages: list[ConversationMessage]) -> list[types.Content]:
    """Convert successful application chat turns into Gemini contents."""
    contents = []
    for message in messages:
        if not message.get("include_in_history", False):
            continue
        message_role = message.get("role")
        if message_role not in {"user", "assistant"}:
            continue
        role = "model" if message_role == "assistant" else "user"
        text = message.get("content", "")
        if not text:
            continue
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part(text=text)],
            )
        )
    return contents


class GeminiService:
    """Encapsulates client setup and communication with the Gemini API."""

    def __init__(self, settings: Settings) -> None:
        try:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        except (errors.APIError, httpx.HTTPError):
            logger.error("Gemini client initialization failed.")
            raise GeminiServiceError(
                "Gemini client could not be initialized."
            ) from None
        self._model = settings.gemini_model
        self._temperature = settings.temperature

    def generate_answer(
        self,
        question: str,
        history: list[ConversationMessage],
    ) -> str:
        """Generate an answer from a question and successful prior turns."""
        question = question.strip()
        if not question:
            raise GeminiServiceError("Question cannot be empty.")

        contents = [
            *_history_contents(history),
            types.Content(role="user", parts=[types.Part(text=question)]),
        ]
        try:
            logger.info("Sending Gemini request using model %s.", self._model)
            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=QA_SYSTEM_INSTRUCTION,
                    temperature=self._temperature,
                ),
            )
        except (errors.APIError, httpx.HTTPError):
            logger.error("Gemini API request failed for model %s.", self._model)
            raise GeminiServiceError("Gemini request failed.") from None

        answer = response.text
        if not answer or not answer.strip():
            logger.warning("Gemini returned an empty answer for model %s.", self._model)
            raise GeminiServiceError("Gemini returned an empty answer.")
        return answer
