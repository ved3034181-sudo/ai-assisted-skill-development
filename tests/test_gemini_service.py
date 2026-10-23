from unittest.mock import MagicMock, patch

import httpx
import pytest
from google.genai import errors

from app.config.settings import Settings
from app.services.gemini_service import GeminiService, GeminiServiceError


@pytest.fixture
def settings() -> Settings:
    return Settings(
        gemini_api_key="test-key",
        gemini_model="gemini-test",
        temperature=0.4,
    )


@patch("app.services.gemini_service.genai.Client")
def test_service_initializes_google_genai_client(
    client_class: MagicMock,
    settings: Settings,
) -> None:
    service = GeminiService(settings)

    client_class.assert_called_once_with(api_key="test-key")
    assert service is not None


@patch("app.services.gemini_service.genai.Client")
def test_initialization_error_is_converted_to_safe_service_error(
    client_class: MagicMock,
    settings: Settings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client_class.side_effect = httpx.ConnectError("private connection detail")

    with pytest.raises(GeminiServiceError, match="could not be initialized"):
        GeminiService(settings)

    assert "private connection detail" not in caplog.text
    assert "test-key" not in caplog.text


@patch("app.services.gemini_service.genai.Client")
def test_sends_question_settings_and_system_instruction(
    client_class: MagicMock,
    settings: Settings,
) -> None:
    client = client_class.return_value
    client.models.generate_content.return_value.text = "An answer"

    answer = GeminiService(settings).generate_answer("What is this?", [])

    assert answer == "An answer"
    request = client.models.generate_content.call_args.kwargs
    assert request["model"] == "gemini-test"
    assert request["contents"][-1].parts[0].text == "What is this?"
    assert request["config"].temperature == 0.4
    assert request["config"].system_instruction


@patch("app.services.gemini_service.genai.Client")
def test_formats_only_successful_conversation_history(
    client_class: MagicMock,
    settings: Settings,
) -> None:
    client = client_class.return_value
    client.models.generate_content.return_value.text = "Follow-up answer"
    history = [
        {"role": "user", "content": "First question", "include_in_history": True},
        {"role": "assistant", "content": "First answer", "include_in_history": True},
        {"role": "user", "content": "Failed question", "include_in_history": False},
        {"role": "tool", "content": "Unsupported role", "include_in_history": True},
    ]

    GeminiService(settings).generate_answer("Follow-up?", history)

    contents = client.models.generate_content.call_args.kwargs["contents"]
    assert [(item.role, item.parts[0].text) for item in contents] == [
        ("user", "First question"),
        ("model", "First answer"),
        ("user", "Follow-up?"),
    ]


@patch("app.services.gemini_service.genai.Client")
def test_empty_question_does_not_call_api(
    client_class: MagicMock,
    settings: Settings,
) -> None:
    with pytest.raises(GeminiServiceError, match="Question cannot be empty"):
        GeminiService(settings).generate_answer("  ", [])

    client_class.return_value.models.generate_content.assert_not_called()


@patch("app.services.gemini_service.genai.Client")
def test_api_failure_raises_safe_service_error(
    client_class: MagicMock,
    settings: Settings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = client_class.return_value
    client.models.generate_content.side_effect = errors.APIError(
        500,
        {"message": "private provider detail"},
        "private provider detail",
    )

    with pytest.raises(GeminiServiceError, match="Gemini request failed") as exc_info:
        GeminiService(settings).generate_answer("Question", [])

    assert "private provider detail" not in str(exc_info.value)
    assert "test-key" not in caplog.text
    assert "private provider detail" not in caplog.text


@patch("app.services.gemini_service.genai.Client")
def test_transport_failure_raises_safe_service_error(
    client_class: MagicMock,
    settings: Settings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = client_class.return_value
    client.models.generate_content.side_effect = httpx.ConnectError(
        "private connection detail"
    )

    with pytest.raises(GeminiServiceError, match="Gemini request failed"):
        GeminiService(settings).generate_answer("Question", [])

    assert "private connection detail" not in caplog.text


@pytest.mark.parametrize("response_text", [None, "", "  "])
@patch("app.services.gemini_service.genai.Client")
def test_empty_response_raises_service_error(
    client_class: MagicMock,
    settings: Settings,
    response_text: str | None,
) -> None:
    client_class.return_value.models.generate_content.return_value.text = response_text

    with pytest.raises(GeminiServiceError, match="empty answer"):
        GeminiService(settings).generate_answer("Question", [])
