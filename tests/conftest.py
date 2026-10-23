from collections.abc import Iterator
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def disable_dotenv_loading() -> Iterator[None]:
    with patch("app.config.settings.load_dotenv"):
        yield
