import pytest


@pytest.fixture
def empty_just():
    return {}


@pytest.fixture
def test_weight():
    return {i: 5 - i for i in range(5)}
