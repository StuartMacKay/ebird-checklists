import datetime as dt

import pytest

from ebird.checklists.models import Observation
from tests.unit.factories import ObservationFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def observation():
    observation = ObservationFactory.create()
    return observation


def test_for_country__observations_fetched(observation):
    country = observation.location.country
    obj = Observation.objects.for_country(country).first()
    assert obj.id == observation.id
    assert obj.location.country == country


def test_for_country_code__observations_fetched(observation):
    country_code = observation.location.country_code
    obj = Observation.objects.for_country(country_code).first()
    assert obj.id == observation.id
    assert obj.location.country_code == country_code


def test_for_state__observations_fetched(observation):
    state = observation.location.state
    obj = Observation.objects.for_state(state).first()
    assert obj.id == observation.id
    assert obj.location.state == state


def test_for_state_code__observations_fetched(observation):
    state_code = observation.location.state_code
    obj = Observation.objects.for_state(state_code).first()
    assert obj.id == observation.id
    assert obj.location.state_code == state_code


def test_for_county__observations_fetched(observation):
    county = observation.location.county
    obj = Observation.objects.for_county(county).first()
    assert obj.id == observation.id
    assert obj.location.county == county


def test_for_county_code__observations_fetched(observation):
    county_code = observation.location.county_code
    obj = Observation.objects.for_county(county_code).first()
    assert obj.id == observation.id
    assert obj.location.county_code == county_code


def test_for_year__observations_fetched(observation):
    year = dt.date.today().year
    observation.checklist.date = observation.checklist.date.replace(year=year)
    observation.checklist.save()
    obj = Observation.objects.for_year(year).first()
    assert obj.id == observation.id
    assert obj.checklist.date.year == year


def test_for_month__observations_fetched(observation):
    date = dt.date.today()
    year, month = date.year, date.month
    observation.checklist.date = observation.checklist.date.replace(
        year=year, month=month
    )
    observation.checklist.save()
    obj = Observation.objects.for_month(year, month).first()
    assert obj.id == observation.id
    assert obj.checklist.date.year == year
    assert obj.checklist.date.month == month


def test_for_day__observations_fetched(observation):
    date = dt.date.today()
    year, month, day = date.year, date.month, date.day
    observation.checklist.date = observation.checklist.date.replace(
        year=year, month=month, day=day
    )
    observation.checklist.save()
    obj = Observation.objects.for_day(year, month, day).first()
    assert obj.id == observation.id
    assert obj.checklist.date.year == year
    assert obj.checklist.date.month == month
    assert obj.checklist.date.day == day


def test_for_date__observations_fetched(observation):
    date = dt.date.today()
    observation.checklist.date = date
    observation.checklist.save()
    obj = Observation.objects.for_date(date).first()
    assert obj.id == observation.id
    assert obj.checklist.date == date
