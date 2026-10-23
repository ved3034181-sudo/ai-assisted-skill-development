from pathlib import Path
from unittest.mock import MagicMock

import pytest
from google.genai import errors
from streamlit.testing.v1 import AppTest

from app.services import gemini_service


APP_ENTRYPOINT = Path(__file__).resolve().parents[1] / "streamlit_app.py"


def test_gemini_failure_shows_safe_message_without_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api_key = "unit-test-api-key"
    provider_detail = "private provider detail"
    client = MagicMock()
    client.models.generate_content.side_effect = errors.APIError(
        500,
        {"message": provider_detail},
        provider_detail,
    )
    client_factory = MagicMock(return_value=client)
    monkeypatch.setattr(gemini_service.genai, "Client", client_factory)
    monkeypatch.setenv("GEMINI_API_KEY", api_key)

    app = AppTest.from_file(APP_ENTRYPOINT).run(timeout=30)
    app.chat_input[0].set_value("Test question").run(timeout=30)

    assert not app.exception
    client_factory.assert_called_once_with(api_key=api_key)
    assert len(client.models.generate_content.call_args_list) == 1
    rendered_text = "\n".join(
        [element.value for element in app.error]
        + [element.value for element in app.markdown]
    )
    assert "couldn't answer just now" in rendered_text
    assert api_key not in rendered_text
    assert provider_detail not in rendered_text


def test_missing_key_message_does_not_expose_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    app = AppTest.from_file(APP_ENTRYPOINT).run(timeout=30)

    assert not app.exception
    rendered_errors = "\n".join(element.value for element in app.error)
    assert "create a `.env` file" in rendered_errors.lower()
