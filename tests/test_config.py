import pytest

from app.config.settings import (
    DEFAULT_GEMINI_MODEL,
    DEFAULT_TEMPERATURE,
    SettingsError,
    load_settings,
)


def test_loads_required_key_and_default_model_and_temperature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("TEMPERATURE", raising=False)

    settings = load_settings()

    assert settings.gemini_api_key == "test-key"
    assert settings.gemini_model == DEFAULT_GEMINI_MODEL
    assert settings.temperature == DEFAULT_TEMPERATURE
    assert "test-key" not in repr(settings)


def test_loads_configured_model_and_temperature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")
    monkeypatch.setenv("TEMPERATURE", "1.25")

    settings = load_settings()

    assert settings.gemini_model == "gemini-test"
    assert settings.temperature == 1.25


def test_missing_api_key_fails_clearly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(SettingsError, match=r"[Cc]reate a `.env` file"):
        load_settings()


@pytest.mark.parametrize("value", ["not-a-number", "-0.1", "2.1", "nan", "inf"])
def test_invalid_temperature_fails(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("TEMPERATURE", value)

    with pytest.raises(SettingsError, match="TEMPERATURE"):
        load_settings()


@pytest.mark.parametrize(("value", "expected"), [("0", 0.0), ("2", 2.0)])
def test_temperature_boundaries_are_valid(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
    expected: float,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("TEMPERATURE", value)

    assert load_settings().temperature == expected
