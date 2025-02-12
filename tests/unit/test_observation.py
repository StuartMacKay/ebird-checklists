import pytest
from dateutil.relativedelta import relativedelta

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


@pytest.fixture
def checklist(observation):
    return observation.checklist


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


def test_for_identifier__checklist_fetched(observation):
    identifier = observation.identifier
    Observation.objects.for_identifier(identifier)


def test_for_date__observations_fetched(checklist):
    date = checklist.date
    obj = Observation.objects.for_date(date).first()
    assert obj.checklist.date == date


def test_for_dates__start_date_observations_fetched(checklist):
    start = checklist.date
    end = checklist.date + relativedelta(days=+1)
    obj = Observation.objects.for_dates(start, end).first()
    assert obj is not None


def test_for_dates__end_date_observations_not_fetched(checklist):
    start = checklist.date + relativedelta(days=-1)
    end = checklist.date
    obj = Observation.objects.for_dates(start, end).first()
    assert obj is None


def test_for_observer__identifier__observations_fetched(observation):
    identifier = observation.observer.identifier
    obj = Observation.objects.for_observer(identifier).first()
    assert obj.observer.identifier == identifier


def test_for_observer__name_exact_match__observations_fetched(observation):
    name = observation.observer.name
    obj = Observation.objects.for_observer(name).first()
    assert obj.observer.name == name


def test_for_observer__name_no_match__observations_fetched(observation):
    name = observation.observer.name
    obj = Observation.objects.for_observer(name.lower()).first()
    assert obj is None


def test_manager_in_region_with_dates(checklist, location):
    code = location.country_code
    start = checklist.date
    end = checklist.date + relativedelta(days=+1)
    obj = Observation.objects.in_region_with_dates(code, start, end).first()
    assert obj.location.country_code == code
    assert obj.checklist.date >= start
    assert obj.checklist.date < end
