import datetime as dt

import pytest

from ebird.checklists.models import Observation
from tests.unit.factories import ObservationFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def observation():
    observation = ObservationFactory.create()
    return observation


@pytest.fixture
def location(observation):
    return observation.location


def test_for_country__checklists_fetched(location):
    code = location.country_code
    obj = Observation.objects.for_country(code).first()
    assert obj.location.country_code == code


def test_for_country__unsupported_code(location):
    with pytest.raises(ValueError):
        Observation.objects.for_country(location.country_code.lower())


def test_for_state__observations_fetched(location):
    code = location.state_code
    obj = Observation.objects.for_state(code).first()
    assert obj.location.state_code == code


def test_for_state__unsupported_code(location):
    with pytest.raises(ValueError):
        Observation.objects.for_state(location.state_code.lower())


def test_for_county__observations_fetched(location):
    code = location.county_code
    obj = Observation.objects.for_county(code).first()
    assert obj.location.county_code == code


def test_for_county__unsupported_code(location):
    with pytest.raises(ValueError):
        Observation.objects.for_county(location.county_code.lower())


def test_for_location__observations_fetched(location):
    identifier = location.identifier
    obj = Observation.objects.for_location(identifier).first()
    assert obj.location.identifier == identifier


def test_for_location__unsupported_code(location):
    with pytest.raises(ValueError):
        Observation.objects.for_location(location.identifier.lower())


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
