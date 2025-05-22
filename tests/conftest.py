import pytest
import os
from pyneuphonic import Neuphonic


@pytest.fixture
def client():
    api_key = os.environ.get("NEUPHONIC_API_KEY")
    base_url = os.environ.get("NEUPHONIC_API_URL")

    assert "qa.api.neuphonic.com" in base_url

    return Neuphonic(api_key=api_key, base_url=base_url)
