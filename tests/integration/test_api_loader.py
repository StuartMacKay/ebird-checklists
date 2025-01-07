import datetime
import pytest

from ebird.checklists.loaders import APILoader

pytestmark = pytest.mark.django_db


def test_load_for_date(api_key, country):
    loader = APILoader(api_key)
    loader.load(country, datetime.date.today())
