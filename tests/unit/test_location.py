import pytest

from ebird.checklists.models import Location
from tests.unit.factories import LocationFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def location():
    return LocationFactory.create()


def test_for_country__locations_fetched(location):
    code = location.country_code
    obj = Location.objects.for_country(code).first()
    assert obj.country_code == code


def test_for_country__unsupported_code(location):
    with pytest.raises(ValueError):
        Location.objects.for_country(location.country_code.lower())


def test_for_state__locations_fetched(location):
    code = location.state_code
    obj = Location.objects.for_state(code).first()
    assert obj.state_code == code


def test_for_state__unsupported_code(location):
    with pytest.raises(ValueError):
        Location.objects.for_state(location.state_code.lower())


def test_for_county__locations_fetched(location):
    code = location.county_code
    obj = Location.objects.for_county(code).first()
    assert obj.county_code == code


def test_for_county__unsupported_code(location):
    with pytest.raises(ValueError):
        Location.objects.for_county(location.county_code.lower())


def test_for_identifier__location_fetched(location):
    identifier = location.identifier
    Location.objects.for_identifier(identifier)


def test_country_choices__list_returned(location):
    result = Location.objects.country_choices()
    assert result == [(location.country_code, location.country)]


def test_country_choice__choice_returned(location):
    result = Location.objects.country_choice(location.country_code)
    assert result == (location.country_code, location.country)


def test_state_choices__list_returned(location):
    result = Location.objects.state_choices(location.country_code)
    assert result == [(location.state_code, location.state)]


def test_state_choice__choice_returned(location):
    result = Location.objects.state_choice(location.state_code)
    assert result == (location.state_code, location.state)


def test_county_choices__list_returned(location):
    result = Location.objects.county_choices(location.state_code)
    assert result == [(location.county_code, location.county)]


def test_county_choice__choice_returned(location):
    result = Location.objects.county_choice(location.county_code)
    assert result == (location.county_code, location.county)
