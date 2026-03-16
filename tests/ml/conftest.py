"""Fixtures for tests/ml/"""
import pytest


@pytest.fixture
def symbol():
    return "BTC"


@pytest.fixture
def days():
    return 120
