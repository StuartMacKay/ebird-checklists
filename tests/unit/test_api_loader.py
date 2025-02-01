import datetime as dt
import decimal

from dateutil.relativedelta import relativedelta

import pytest

from ebird.checklists.loaders import APILoader
from ebird.checklists.loaders.utils import str2date
from ebird.checklists.models import Checklist, Observation, Location, Observer, Species

pytestmark = pytest.mark.django_db


def datetime2str(date):
    return date.strftime("%Y-%m-%d %H:%M")


@pytest.fixture
def start():
    return dt.datetime.now().replace(second=0, microsecond=0)


@pytest.fixture
def submitted(start):
    return start + relativedelta(hours=2)


@pytest.fixture
def webowl():
    return {
         "sciName": "Tyto alba",
         "comName": "Western Barn Owl",
         "speciesCode": "webowl",
         "category": "species",
         "taxonOrder": 8516.0,
         "bandingCodes": [],
         "comNameCodes": ["CBOW", "EBOW", "WBOW"],
         "sciNameCodes": ["TYAL"],
         "order": "Strigiformes",
         "familyCode": "tytoni1",
         "familyComName": "Barn-Owls",
         "familySciName": "Tytonidae",
    }


@pytest.fixture
def grhowl():
    return {
        "sciName": "Bubo virginianus",
        "comName": "Great Horned Owl",
        "speciesCode": "grhowl",
        "category": "species",
        "taxonOrder": 8811.0,
        "bandingCodes": ["GHOW"],
        "comNameCodes": [],
        "sciNameCodes": ["BUVI"],
        "order": "Strigiformes",
        "familyCode": "strigi1",
        "familyComName": "Owls",
        "familySciName": "Strigidae"
    }


@pytest.fixture
def species(webowl, grhowl):
    return {
        webowl["speciesCode"]: webowl,
        grhowl["speciesCode"]: grhowl,
    }


@pytest.fixture
def observation():
    return {
        "projId": "EBIRD",
        "speciesCode": "webowl",
        "present": False,
        "obsId": "OBS0000000001",
        "howManyStr": "1",
    }


@pytest.fixture
def observations(observation):
    return [
        observation,
        {
            "projId": "EBIRD",
            "speciesCode": "grhowl",
            "present": False,
            "obsId": "OBS0000000002",
            "howManyStr": "1",
        }
    ]

@pytest.fixture
def observer():
    return {
        "userDisplayName": "Etta Lemon",
    }


@pytest.fixture
def location():
    return {
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


@pytest.fixture
def visit(start, location, observer):
    return {
        "locId": "L901738",
        "subId": "S000000001",
        "userDisplayName": observer["userDisplayName"],
        "numSpecies": 2,
        "obsDt": start.strftime("%d %b %Y"),
        "obsTime": start.strftime("%H:%M"),
        "isoObsDate": datetime2str(start),
        "loc": location
    }

@pytest.fixture
def checklist(start, submitted, observer, observations):
    return {
        "projId": "EBIRD",
        "checklistId": "CL00001",
        "subId": "S000000001",
        "locId": "L901738",
        "creationDt": datetime2str(submitted),
        "lastEditedDt": datetime2str(submitted),
        "obsDt": datetime2str(start),
        "obsTimeValid": True,
        "protocolId": "P22",
        "effortDistanceKm": "1.2",
        "durationHrs": 1.0,
        "allObsReported": False,
        "numObservers": 1,
        "subnational1Code": "US-NY",
        "userDisplayName": observer["userDisplayName"],
        "numSpecies": 1,
        "obs": observations
    }

@pytest.fixture
def loader(settings):
    return APILoader(settings.EBIRD_API_KEY, settings.EBIRD_LOCALE)


@pytest.fixture(autouse=True)
def mock_api_calls(monkeypatch, species):
    def mock_fetch_species(self, code, locale):
        return species[code]

    monkeypatch.setattr(APILoader, "fetch_species", mock_fetch_species)


def test_add_checklist__checklist_added(loader, checklist):
    """If the checklist does not exist, it is added to the database."""
    identifier = checklist["subId"]
    loader.add_checklist(checklist)
    Checklist.objects.get(identifier=identifier)


def test_add_checklist__loader_added(loader, checklist):
    """The added checklist is recorded by the loader"""
    loader.add_checklist(checklist)
    assert loader.added == 1


def test_add_checklist__checklist_updated(loader, submitted, checklist):
    """If the checklist edited, it is updated."""
    chk1 = loader.add_checklist(checklist)
    checklist["numObservers"] += 1
    chk2 = loader.add_checklist(checklist)
    assert chk1.pk == chk2.pk
    assert chk1.observer_count != chk2.observer_count


def test_add_checklist__time_set(loader, checklist, start):
    """A checklist may contain only a date."""
    chk = loader.add_checklist(checklist)
    assert chk.time == start.time()


def test_add_checklist__time_is_optional(loader, checklist):
    """A checklist may contain only a date."""
    checklist["obsTimeValid"] = False
    chk = loader.add_checklist(checklist)
    assert chk.date == str2date(checklist["obsDt"])
    assert chk.time is None


def test_add_checklist__duration_minutes(loader, checklist):
    """The duration field converted to minutes"""
    checklist["durationHrs"] = 2.0
    chk = loader.add_checklist(checklist)
    assert chk.duration == 120


def test_add_checklist__duration_optional(loader, checklist):
    """The duration field is optional"""
    del checklist["durationHrs"]
    chk = loader.add_checklist(checklist)
    assert chk.duration is None


def test_add_checklist__observers_set(loader, checklist):
    """The numObservers field is optional"""
    chk = loader.add_checklist(checklist)
    assert chk.observer_count is checklist["numObservers"]


def test_add_checklist__observers_optional(loader, checklist):
    """The numObservers field is optional"""
    del checklist["numObservers"]
    chk = loader.add_checklist(checklist)
    assert chk.observer_count is None


def test_add_checklist__distance_rounded(loader, checklist):
    """Ensure floats are converted to Decimal and rounded to three places.
    Decimal(1.2) actually generates Decimal('1.199999999999999955591079...')
    """
    checklist["effortDistanceKm"] = 1.2
    chk = loader.add_checklist(checklist)
    assert chk.distance == decimal.Decimal("1.200")


def test_add_checklist__distance_required(loader, checklist):
    """Checklists following the Traveling protocol must have distance set."""
    del checklist["effortDistanceKm"]
    with pytest.raises(KeyError):
        loader.add_checklist(checklist)


def test_add_checklist__distance_optional(loader, checklist):
    """Distance is ignored for checklists not following the travelling protocol."""
    checklist["protocolId"] = "P21"
    chk = loader.add_checklist(checklist)
    assert chk.distance is None


def test_add_checklist__area_rounded(loader, checklist):
    """Ensure floats are converted to Decimal and rounded to three places.
    Decimal(1.1999) actually generates Decimal('1.199899999999999966604...')
    """
    checklist["protocolId"] = "P23"
    checklist["effortAreaHa"] = 1.1999
    chk = loader.add_checklist(checklist)
    assert chk.area == decimal.Decimal("1.200")


def test_add_checklist__area_required(loader, checklist):
    """Checklists following the Area protocol must have area covered set."""
    checklist["protocolId"] = "P23"
    with pytest.raises(KeyError):
        loader.add_checklist(checklist)


def test_add_checklist__area_optional(loader, checklist):
    """Area is ignored for checklists not following the area protocol."""
    checklist["protocolId"] = "P21"
    checklist["effortAreaHa"] = 1.2
    chk = loader.add_checklist(checklist)
    assert chk.area is None


def test_add_checklist__observations_added(loader, checklist, observation):
    """The observations from the checklist are added to the database."""
    chk = loader.add_checklist(checklist)
    obs = Observation.objects.get(identifier=observation["obsId"])
    assert obs.checklist == chk


def test_add_checklist__observations_updated(loader, submitted, checklist, observation):
    """Observations are updated."""
    loader.add_checklist(checklist)
    observation["howManyStr"] = "2"
    loader.add_checklist(checklist)
    obs = Observation.objects.get(identifier=observation["obsId"])
    assert obs.count == 2


def test_add_checklist__observations_deleted(loader, submitted, checklist, observations):
    """If checklist observations are deleted, the records are removed."""
    loader.add_checklist(checklist)
    del observations[0]
    edited = datetime2str(submitted + relativedelta(hours=2))
    checklist["lastEditedDt"] = edited
    loader.add_checklist(checklist)
    ob = Observation.objects.get()
    assert ob.identifier == observations[0]["obsId"]


def test_add_checklist__location_added(loader, checklist):
    """The location is created if it does not exist."""
    identifier = checklist["locId"]
    loader.add_checklist(checklist)
    Location.objects.get(identifier=identifier)


def test_add_checklist__observer_added(loader, checklist):
    """The observer is created if it does not exist."""
    name = checklist["userDisplayName"]
    loader.add_checklist(checklist)
    Observer.objects.get(name=name)


def test_add_location__location_added(loader, location):
    """The location is added to the database."""
    identifier = location["locId"]
    loader.add_location(location)
    Location.objects.get(identifier=identifier)


def test_add_location__location_updated(loader, location):
    """If the location exists, then it is updated."""
    loc1 = loader.add_location(location)
    location["name"] = "Woodpecker Woods Rd."
    loc2 = loader.add_location(location)
    assert loc1.pk == loc2.pk
    assert loc1.name != loc2.name


def test_add_observation__observation_added(loader, visit, observation):
    """The observation is added to the database."""
    identifier = observation["obsId"]
    chk = loader.add_visit(visit)
    loader.add_observation(observation, chk)
    assert Observation.objects.get(identifier=identifier)


def test_add_observation__observation_updated(loader, checklist, observation):
    """The observation is updated. Note this bypasses the edited field check."""
    chk = loader.add_checklist(checklist)
    obs1 = loader.add_observation(observation, chk)
    observation["howManyStr"] = str(obs1.count + 1)
    obs2 = loader.add_observation(observation, chk)
    assert obs1.pk == obs2.pk
    assert obs1.count != obs2.count


def test_add_observation__count_optional(loader, checklist, observation, location):
    """If a count is not given, then it is None"""
    observation["howManyStr"] = 'X'
    loader.add_checklist(checklist)
    obs = Observation.objects.get(identifier=observation["obsId"])
    assert obs.count is None


def test_add_observer__observer_created(loader, observer):
    """An observer is added to the database."""
    obsr = loader.add_observer(observer)
    assert obsr.name == observer["userDisplayName"]


def test_add_observer__existing_observer_returned(loader, observer):
    """The observer's name is used as an identifier"""
    loader.add_observer(observer)
    loader.add_observer(observer)
    Observer.objects.get(name=observer["userDisplayName"])


def test_add_visit__checklist_added(loader, visit):
    """If the checklist does not exist, it is added to the database."""
    identifier = visit["subId"]
    loader.add_visit(visit)
    Checklist.objects.get(identifier=identifier)


def test_add_visit__location_added(loader, visit):
    """When a visits is added, the Location is also added."""
    identifier = visit["loc"]["locId"]
    loader.add_visit(visit)
    Location.objects.get(identifier=identifier)


def test_add_visit__observer_added(loader, visit):
    """When a visits is added, the Observer is also added."""
    name = visit["userDisplayName"]
    loader.add_visit(visit)
    Observer.objects.get(name=name)


def test_add_visit__checklist_unchanged(loader, visit):
    """If the visit is added again, the record is not updated."""
    loader.add_visit(visit)
    visit["numSpecies"] += 1
    checklist = loader.add_visit(visit)
    assert checklist is None


def test_add_visit__time_optional(loader, visit):
    """Incidental or historical visits may not include time."""
    del visit["obsTime"]
    chk = loader.add_visit(visit)
    assert chk.time is None


def test_add_species__species_added(loader, webowl):
    """The Species is added to the database."""
    obj = loader.add_species(webowl)
    assert obj.species_code == webowl["speciesCode"]
