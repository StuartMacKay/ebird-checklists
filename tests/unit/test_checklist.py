import datetime as dt

import pytest
from dateutil.relativedelta import relativedelta

from ebird.checklists.models import Checklist
from tests.unit.factories import ChecklistFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def checklist():
    return ChecklistFactory.create()


@pytest.fixture
def location(checklist):
    return checklist.location


def test_for_country_code__checklists_fetched(location):
    code = location.country_code
    obj = Checklist.objects.for_country(code).first()
    assert obj.location.country_code == code


def test_for_country__unsupported_code(location):
    with pytest.raises(ValueError):
        Checklist.objects.for_country(location.country_code.lower())


def test_for_state_code__checklists_fetched(location):
    code = location.state_code
    obj = Checklist.objects.for_state(code).first()
    assert obj.location.state_code == code


def test_for_state__unsupported_code(location):
    with pytest.raises(ValueError):
        Checklist.objects.for_state(location.state_code.lower())


def test_for_county_code__checklists_fetched(location):
    code = location.county_code
    obj = Checklist.objects.for_county(code).first()
    assert obj.location.county_code == code


def test_for_county__unsupported_code(location):
    with pytest.raises(ValueError):
        Checklist.objects.for_county(location.county_code.lower())


def test_for_location__checklists_fetched(location):
    identifier = location.identifier
    obj = Checklist.objects.for_location(identifier).first()
    assert obj.location.identifier == identifier


def test_for_location__unsupported_code(location):
    with pytest.raises(ValueError):
        Checklist.objects.for_location(location.identifier.lower())


def test_for_identifier__checklist_fetched(checklist):
    identifier = checklist.identifier
    Checklist.objects.for_identifier(identifier)


def test_for_date__checklists_fetched(checklist):
    date = checklist.date
    obj = Checklist.objects.for_date(date).first()
    assert obj.date == date


def test_for_dates__start_date_checklists_fetched(checklist):
    start = checklist.date
    end = checklist.date + relativedelta(days=+1)
    obj = Checklist.objects.for_dates(start, end).first()
    assert obj is not None


def test_for_dates__end_date_checklists_not_fetched(checklist):
    start = checklist.date + relativedelta(days=-1)
    end = checklist.date
    obj = Checklist.objects.for_dates(start, end).first()
    assert obj is None


def test_for_protocol__checklists_fetched(checklist):
    code = checklist.protocol_code
    obj = Checklist.objects.for_protocol(code).first()
    assert obj.protocol_code == code


def test_for_protocol__unsupported_code(checklist):
    with pytest.raises(ValueError):
        Checklist.objects.for_location(checklist.protocol_code.lower())


def test_for_observer__identifier__checklists_fetched(checklist):
    identifier = checklist.observer.identifier
    obj = Checklist.objects.for_observer(identifier).first()
    assert obj.observer.identifier == identifier


def test_for_observer__name_exact_match__checklists_fetched(checklist):
    name = checklist.observer.name
    obj = Checklist.objects.for_observer(name).first()
    assert obj.observer.name == name


def test_for_observer__name_no_match__checklists_fetched(checklist):
    name = checklist.observer.name
    obj = Checklist.objects.for_observer(name.lower()).first()
    assert obj is None


def test_for_hotspot__checklists_fetched(location):
    location.hotspot = True
    location.save()
    obj = Checklist.objects.for_hotspots().first()
    assert obj is not None


def test_for_hotspot__checklists_not_fetched(location):
    location.hotspot = False
    location.save()
    obj = Checklist.objects.for_hotspots().first()
    assert obj is None


def test_complete__checklists_fetched(checklist):
    checklist.complete = True
    checklist.save()
    obj = Checklist.objects.complete().first()
    assert obj is not None


def test_complete__checklists_not_fetched(checklist):
    checklist.complete = False
    checklist.save()
    obj = Checklist.objects.complete().first()
    assert obj is None


def test_manager_in_region_with_dates(checklist, location):
    code = location.country_code
    start = checklist.date
    end = checklist.date + relativedelta(days=+1)
    obj = Checklist.objects.in_region_with_dates(code, start, end).first()
    assert obj.location.country_code == code
    assert obj.date >= start
    assert obj.date < end
