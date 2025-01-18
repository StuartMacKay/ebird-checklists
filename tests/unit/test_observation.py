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


def test_for_date__observations_fetched(observation):
    date = dt.date.today()
    observation.checklist.date = date
    observation.checklist.save()
    obj = Observation.objects.for_date(date).first()
    assert obj.checklist.date == date
