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
