import math
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"
DEFAULT_TEMPERATURE = 0.2
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0


class SettingsError(ValueError):
    """Raised when required application configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = field(repr=False)
    gemini_model: str
    temperature: float


def _configured_gemini_model() -> str:
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
    return model or DEFAULT_GEMINI_MODEL


def get_gemini_model() -> str:
    """Load environment configuration and return the selected model name."""
    load_dotenv()
    return _configured_gemini_model()


def load_settings() -> Settings:
    """Load and validate the Gemini API key, model, and temperature."""
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SettingsError(
            "Gemini is not configured. Create a `.env` file in the project folder "
            "and set `GEMINI_API_KEY` to your Gemini API key."
        )

    temperature_value = os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE))
    try:
        temperature = float(temperature_value)
    except ValueError as exc:
        raise SettingsError("TEMPERATURE must be a number from 0 to 2.") from exc

    if (
        not math.isfinite(temperature)
        or not MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE
    ):
        raise SettingsError("TEMPERATURE must be a number from 0 to 2.")

    return Settings(
        gemini_api_key=api_key,
        gemini_model=_configured_gemini_model(),
        temperature=temperature,
    )
