import datetime
import pytest

from ebird.checklists.loaders import APILoader

pytestmark = pytest.mark.django_db


def test_load_checklists(api_key, locale, country):
    loader = APILoader(api_key, locale)
    loader.load_checklists(country, datetime.date.today())


def test_update_checklists(api_key, locale, country):
    loader = APILoader(api_key, locale)
    loader.load_checklists(country, datetime.date.today())
    loader.update_checklists(datetime.date.today())
