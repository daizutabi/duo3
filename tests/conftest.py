import pytest

import duo3.sentence


@pytest.fixture(scope="session")
def sentences():
    yield duo3.sentence.read()
