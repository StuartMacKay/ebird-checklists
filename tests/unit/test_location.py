import pytest

from ebird.checklists.models import Location
from tests.unit.factories import LocationFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def location():
    return LocationFactory.create()


def test_for_country__locations_fetched(location):
    code = location.country.code
    obj = Location.objects.for_country(code).first()
    assert obj.country.code == code


def test_for_country__unsupported_code(location):
    with pytest.raises(ValueError):
        Location.objects.for_country(location.country.code.lower())


def test_for_region_locations_fetched(location):
    code = location.region.code
    obj = Location.objects.for_region(code).first()
    assert obj.region.code == code


def test_for_region__unsupported_code(location):
    with pytest.raises(ValueError):
        Location.objects.for_region(location.region.code.lower())


def test_for_district__locations_fetched(location):
    code = location.district.code
    obj = Location.objects.for_district(code).first()
    assert obj.district.code == code


def test_for_district__unsupported_code(location):
    with pytest.raises(ValueError):
        Location.objects.for_district(location.district.code.lower())


def test_for_identifier__location_fetched(location):
    identifier = location.identifier
    Location.objects.for_identifier(identifier)
