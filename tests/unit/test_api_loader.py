from datetime import datetime

import pytest

from ebird.checklists.loaders import APILoader, api
from ebird.checklists.models import Checklist, Observation

pytestmark = pytest.mark.django_db


@pytest.fixture
def visits():
    return [
        {
            "locId": "L901738",
            "subId": "S000000001",
            "userDisplayName": "Etta Lemon",
            "numSpecies": 2,
            "obsDt": "01 Jan 2025",
            "obsTime": "08:00",
            "isoObsDate": "2025-01-01 08:00",
            "loc": {
                "locId": "L901738",
                "name": "Sapsucker Woods Rd.",
                "latitude": "42.4749141",
                "longitude": "-76.4503813",
                "countryCode": "US",
                "countryName": "United States",
                "subnational1Name": "New York",
                "subnational1Code": "US-NY",
                "subnational2Code": "US-NY-109",
                "subnational2Name": "Tompkins",
                "isHotspot": True,
            }
        }
    ]

@pytest.fixture
def checklist():
    return {
        "projId": "EBIRD",
        "checklistId": "CL00001",
        "subId": "S000000001",
        "locId": "L901738",
        "creationDt": "2025-01-01 12:00",
        "lastEditedDt": "2025-01-01 12:00",
        "obsDt": "2025-01-01 08:00",
        "obsTimeValid": True,
        "protocolId": "P22",
        "effortDistanceKm": "1.2",
        "allObsReported": False,
        "numObservers": 1,
        "subnational1Code": "US-NY",
        "userDisplayName": "Etta Lemon",
        "numSpecies": 1,
        "obs": [
            {
                "projId": "EBIRD",
                "speciesCode": "webowl1",
                "present": False,
                "obsId": "OBS0000000001",
                "howManyStr": "1",
            },
            {
                "projId": "EBIRD",
                "speciesCode": "grhowl",
                "present": False,
                "obsId": "OBS0000000002",
                "howManyStr": "1",
            }
        ],
    }


@pytest.fixture
def date(checklist):
    return datetime.strptime(checklist["obsDt"], "%Y-%m-%d %H:%M")

@pytest.fixture
def mock_api_calls(monkeypatch, visits, checklist, date):
    def mock_get_visits(api_key, region, date=None, max_results=None):
        return visits

    def mock_fetch_checklist(self, identifier):
        return checklist

    monkeypatch.setattr(api, "get_visits", mock_get_visits)
    monkeypatch.setattr(APILoader, "fetch_checklist", mock_fetch_checklist)


def test_checklist_added(mock_api_calls, settings, visits, checklist, date):
    loader = APILoader(settings.EBIRD_API_KEY)
    loader.load_checklists("US-NY", date)
    Checklist.objects.get(identifier=checklist["subId"])


def test_observations_added(mock_api_calls, settings, visits, checklist, date):
    loader = APILoader(settings.EBIRD_API_KEY)
    loader.load_checklists("US-NY", date)
    Observation.objects.get(identifier=checklist["obs"][0]["obsId"])
    Observation.objects.get(identifier=checklist["obs"][1]["obsId"])


def test_checklist_updated(mock_api_calls, settings, visits, checklist, date):
    """If the lastEditedDt is later than the Checklist's edited field
    then the checklist is updated."""
    loader = APILoader(settings.EBIRD_API_KEY)
    loader.load_checklists("US-NY", date)

    checklist["numObservers"] = 2
    checklist["lastEditedDt"] = "2025-01-01 18:00"

    loader.load_checklists("US-NY", date)
    obj = Checklist.objects.get(identifier=checklist["subId"])
    assert obj.observer_count == 2


def test_checklist_unchanged(mock_api_calls, settings, visits, checklist, date):
    """If the lastEditedDt is the same as the Checklist's edited field
    then the checklist is not updated."""
    loader = APILoader(settings.EBIRD_API_KEY)
    loader.load_checklists("US-NY", date)

    checklist["numObservers"] = 2

    loader.load_checklists("US-NY", date)
    obj = Checklist.objects.get(identifier=checklist["subId"])
    assert obj.observer_count == 1


def test_observation_updated(mock_api_calls, settings, visits, checklist, date):
    """If the lastEditedDt is later than the Checklist's edited field
    then the checklist is updated."""
    loader = APILoader(settings.EBIRD_API_KEY)
    loader.load_checklists("US-NY", date)

    checklist["obs"][0]["howManyStr"] = "2"
    checklist["lastEditedDt"] = "2025-01-01 18:00"

    loader.load_checklists("US-NY", date)
    observation = Observation.objects.get(identifier= checklist["obs"][0]["obsId"])
    assert observation.count == 2


def test_orphaned_observation_deleted(mock_api_calls, settings, visits, checklist, date):
    """If an observation is deleted from the eBird checklist then it is
    also deleted from the database."""
    loader = APILoader(settings.EBIRD_API_KEY)
    loader.load_checklists("US-NY", date)

    del checklist["obs"][1]
    checklist["lastEditedDt"] = "2025-01-01 18:00"

    loader.load_checklists("US-NY", date)
    obj = Checklist.objects.get(identifier=checklist["subId"])
    assert obj.observations.count() == 1
