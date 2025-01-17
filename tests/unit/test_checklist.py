import datetime as dt

import pytest

from ebird.checklists.models import Checklist
from tests.unit.factories import ChecklistFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def checklist():
    return ChecklistFactory.create()


@pytest.fixture
def location(checklist):
    return checklist.location


def test_for_country__checklists_fetched(location):
    code = location.country_code
    obj = Checklist.objects.for_country(code).first()
    assert obj.location.country_code == code


def test_for_country__unsupported_code(location):
    with pytest.raises(ValueError):
        Checklist.objects.for_country(location.country_code.lower())


def test_for_state__checklists_fetched(location):
    code = location.state_code
    obj = Checklist.objects.for_state(code).first()
    assert obj.location.state_code == code


def test_for_state__unsupported_code(location):
    with pytest.raises(ValueError):
        Checklist.objects.for_state(location.state_code.lower())


def test_for_country_code__checklists_fetched(checklist):
    country_code = checklist.location.country_code
    obj = Checklist.objects.for_country(country_code).first()
    assert obj.id == checklist.id
    assert obj.location.country_code == country_code


def test_for_state__checklists_fetched(checklist):
    state = checklist.location.state
    obj = Checklist.objects.for_state(state).first()
    assert obj.id == checklist.id
    assert obj.location.state == state


def test_for_state_code__checklists_fetched(checklist):
    state_code = checklist.location.state_code
    obj = Checklist.objects.for_state(state_code).first()
    assert obj.id == checklist.id
    assert obj.location.state_code == state_code


def test_for_county__checklists_fetched(checklist):
    county = checklist.location.county
    obj = Checklist.objects.for_county(county).first()
    assert obj.id == checklist.id
    assert obj.location.county == county


def test_for_county_code__checklists_fetched(checklist):
    county_code = checklist.location.county_code
    obj = Checklist.objects.for_county(county_code).first()
    assert obj.id == checklist.id
    assert obj.location.county_code == county_code


def test_for_year__checklists_fetched(checklist):
    year = dt.date.today().year
    checklist.date = checklist.date.replace(year=year)
    checklist.save()
    obj = Checklist.objects.for_year(year).first()
    assert obj.id == checklist.id
    assert obj.date.year == year


def test_for_month__checklists_fetched(checklist):
    date = dt.date.today()
    year, month = date.year, date.month
    checklist.date = checklist.date.replace(year=year, month=month)
    checklist.save()
    obj = Checklist.objects.for_month(year, month).first()
    assert obj.id == checklist.id
    assert obj.date.year == year
    assert obj.date.month == month


def test_for_day__checklists_fetched(checklist):
    date = dt.date.today()
    year, month, day = date.year, date.month, date.day
    checklist.date = checklist.date.replace(year=year, month=month, day=day)
    checklist.save()
    obj = Checklist.objects.for_day(year, month, day).first()
    assert obj.id == checklist.id
    assert obj.date.year == year
    assert obj.date.month == month
    assert obj.date.day == day


def test_for_date__checklists_fetched(checklist):
    date = dt.date.today()
    checklist.date = date
    checklist.save()
    obj = Checklist.objects.for_date(date).first()
    assert obj.id == checklist.id
    assert obj.date == date
