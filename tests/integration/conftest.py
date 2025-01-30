import os

import pytest
from faker import Faker


@pytest.fixture(scope="session")
def api_key():
    return os.environ["EBIRD_API_KEY"]


@pytest.fixture(scope="session")
def locale():
    return os.environ["EBIRD_LOCALE"]


@pytest.fixture(scope="session")
def country():
    return Faker().country_code()
