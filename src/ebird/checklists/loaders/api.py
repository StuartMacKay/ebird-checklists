import datetime as dt
import decimal
import logging
import re
from urllib.error import HTTPError, URLError

from django.utils.timezone import get_default_timezone
from ebird.api import get_checklist, get_location, get_regions, get_visits, get_taxonomy

from .utils import str2datetime, float2int, str2decimal
from ..models import Checklist, Location, Observation, Observer, Species

logger = logging.getLogger(__name__)


class APILoader:
    """
    The APILoader downloads checklists from the eBird API and saves
    them to the database.

    Arguments:

        api_key: Your key to access the eBird API.
            Your can request a key at https://ebird.org/data/download.
            You will need an eBird account to do so.

        locale: The language to load for Species common names.
            The default is English.. ebird.api.get_taxonomy_locales returns
            the complete list of languages supported by eBird.

    The eBird API limits the number of records returned to 200. When downloading
    the visits for a given region if 200 hundred records are returned then it is
    assumed there are more and the loader will fetch the sub-regions and download
    the visits for each, repeating the process if necessary. To give an extreme
    example if you download the visits for the United State, "US" then the API
    will always return 200 results and the loader then download the visits to
    each of the 50 states and then each of the 3143 counties. DON'T DO THIS.
    Even if you don't get banned, karma will ensure bad things happen to you.

    """

    def __init__(self, api_key: str, locale: str):
        self.api_key: str = api_key
        self.locale: str = locale
        self.visits: list = []
        self.checklists: list = []
        self.added: int = 0

    @staticmethod
    def has_checklist(identifier: str) -> bool:
        return Checklist.objects.filter(identifier=identifier).exists()

    def add_checklist(self, data: dict) -> Checklist:
        identifier = data["subId"]
        created: dt.datetime = str2datetime(data["creationDt"])
        edited: dt.datetime = str2datetime(data["lastEditedDt"])
        started: dt.datetime = str2datetime(data["obsDt"])

        time: dt.time | None = None
        if data["obsTimeValid"]:
            time = started.time()

        duration: str | None = None
        if "durationHrs" in data:
            duration = float2int(data["durationHrs"] * 60.0)

        values = {
            "created": created,
            "edited": edited,
            "location": self.get_location(data),
            "observer": self.get_observer(data),
            "group": "",
            "species_count": data["numSpecies"],
            "date": started.date(),
            "time": time,
            "started": started,
            "protocol": "",
            "protocol_code": data["protocolId"],
            "project_code": data["projId"],
            "duration": duration,
            "complete": data["allObsReported"],
            "comments": "",
            "url": "https://ebird.org/checklist/%s" % identifier,
        }

        if "numObservers" in data:
            values["observer_count"] = int(data["numObservers"])

        if data["protocolId"] == "P22":
            dist = data["effortDistanceKm"]
            values["distance"] = round(decimal.Decimal(dist), 3)
        elif data["protocolId"] == "P23":
            area = data["effortAreaHa"]
            values["area"] = round(decimal.Decimal(area), 3)

        if checklist := Checklist.objects.filter(identifier=identifier).first():
            for key, value in values.items():
                setattr(checklist, key, value)
            checklist.save()
        else:
            checklist = Checklist.objects.create(identifier=identifier, **values)

        self.added += 1

        for observation_data in data["obs"]:
            self.add_observation(observation_data, checklist)

        for observation in checklist.observations.filter(edited__lt=edited):
            logger.info(
                "Deleting observation: %s",
                identifier,
                extra={
                    "identifier": identifier,
                    "species": observation.species.common_name,
                    "count": observation.count,
                },
            )
            observation.delete()

        return checklist

    @staticmethod
    def add_location(data: dict) -> Location:
        identifier: str = data["locId"]
        values: dict = {
            "identifier": identifier,
            "type": "",
            "name": data["name"],
            "county": data.get("subnational2Name", ""),
            "county_code": data.get("subnational2Code", ""),
            "state": data["subnational1Name"],
            "state_code": data["subnational1Code"],
            "country": data["countryName"],
            "country_code": data["countryCode"],
            "iba_code": "",
            "bcr_code": "",
            "usfws_code": "",
            "atlas_block": "",
            "latitude": str2decimal(data["latitude"]),
            "longitude": str2decimal(data["longitude"]),
            "url": "https://ebird.org/region/%s" % identifier,
        }

        if location := Location.objects.filter(identifier=identifier).first():
            for key, value in values.items():
                setattr(location, key, value)
            location.save()
        else:
            location = Location.objects.create(**values)

        return location

    def add_observation(self, data: dict, checklist: Checklist) -> Observation:
        identifier: str = data["obsId"]
        count: int | None
        observation: Observation

        if re.match(r"\d+", data["howManyStr"]):
            count = float2int(data["howManyStr"])
            if count == 0:
                count = None
        else:
            count = None

        values: dict = {
            "edited": checklist.edited,
            "identifier": identifier,
            "checklist": checklist,
            "location": checklist.location,
            "observer": checklist.observer,
            "species": self.get_species(data),
            "count": count,
            "breeding_code": "",
            "breeding_category": "",
            "behavior_code": "",
            "age_sex": "",
            "media": False,
            "approved": None,
            "reviewed": None,
            "reason": "",
            "comments": "",
            "urn": self.get_urn(data),
        }

        if observation := Observation.objects.filter(identifier=identifier).first():
            for key, value in values.items():
                setattr(observation, key, value)
            observation.save()
        else:
            observation = Observation.objects.create(**values)
        return observation

    @staticmethod
    def add_observer(data: dict) -> Observer:
        name: str = data["userDisplayName"]
        observer, created = Observer.objects.get_or_create(name=name)
        return observer

    def add_visit(self, data: dict) -> Checklist | None:
        identifier = data["subId"]

        if self.has_checklist(identifier):
            return

        started: dt.datetime = dt.datetime.strptime(data["obsDt"], "%d %b %Y").replace(
            tzinfo=get_default_timezone()
        )
        date: dt.date = started.date()
        time: dt.time | None = None

        if "obsTime" in data:
            time = started.time()

        values = {
            "location": self.add_location(data["loc"]),
            "observer": self.add_observer(data),
            "group": "",
            "species_count": data["numSpecies"],
            "date": date,
            "time": time,
            "started": started,
            "protocol": "",
            "protocol_code": "",
            "project_code": "",
            "comments": "",
            "url": "https://ebird.org/checklist/%s" % identifier,
        }

        checklist = Checklist.objects.create(identifier=identifier, **values)
        self.checklists.append(identifier)

        return checklist

    @staticmethod
    def add_species(data: dict) -> Species:
        code = data["speciesCode"]

        values = {
            "taxon_order": int(data["taxonOrder"]),
            "order": data.get("order", ""),
            "category": data["category"],
            "family_code": data.get("familyCode", ""),
            "common_name": data["comName"],
            "scientific_name": data["sciName"],
            "family_common_name": data.get("familyComName", ""),
            "family_scientific_name": data.get("familySciName", ""),
            "subspecies_common_name": "",
            "subspecies_scientific_name": "",
            "exotic_code": "",
        }

        if species := Species.objects.filter(species_code=code).first():
            for key, value in values.items():
                species.setattr(key, value)
            species.save()
        else:
            species = Species.objects.create(species_code=code, **values)

        return species

    @staticmethod
    def get_urn(row: dict[str, str]) -> str:
        return f"URN:CornellLabOfOrnithology:{row['projId']}:{row['obsId']}"

    def get_location(self, data: dict) -> Location:
        identifier: str = data["locId"]
        location = Location.objects.filter(identifier=identifier).first()
        if location is None:
            location = self.load_location(identifier)
        return location

    @staticmethod
    def get_observer(data: dict) -> Observer:
        name: str = data["userDisplayName"]
        observer = Observer.objects.filter(name=name).first()
        if observer is None:
            observer = Observer.objects.create(name=name)
            logger.error("Observer did not exist", extra={"observer": name})
        return observer

    def get_species(self, data: dict) -> Species:
        code = data["speciesCode"]
        if (species := Species.objects.filter(species_code=code).first()) is None:
            species = self.load_species(code, self.locale)
        return species

    def fetch_checklist(self, identifier: str) -> dict:
        data = get_checklist(self.api_key, identifier)
        return data

    def fetch_species(self, code: str, locale: str) -> dict:
        return get_taxonomy(self.api_key, locale=locale, species=code)[0]

    def fetch_subregions(self, region: str) -> list[str]:
        logger.info(
            "Fetching sub-regions: %s",
            region,
            extra={"region": region},
        )
        region_types = ["subnational1", "subnational2", None]
        levels: int = len(region.split("-", 2))
        region_type = region_types[levels - 1]

        if region_type:
            items = get_regions(self.api_key, region_type, region)
            sub_regions = [item["code"] for item in items]
        else:
            sub_regions = []

        return sub_regions

    def fetch_visits(self, region: str, date: dt.date = None):
        visits: list = get_visits(self.api_key, region, date=date, max_results=200)
        if len(visits) == 200:
            if sub_regions := self.fetch_subregions(region):
                for sub_region in sub_regions:
                    logger.info(
                        "Loading checklists for sub-regions: %s, %s",
                        sub_region,
                        date,
                        extra={"region": sub_region, "date": date},
                    )
                    self.fetch_visits(sub_region, date)
            else:
                # No more sub-regions, just add the 200 visits
                logger.warning(
                    "Loading checklists - API limit reached: %s, %s",
                    region,
                    date,
                    extra={"region": region, "date": date},
                )
                for visit in visits:
                    self.visits.append(visit)

        else:
            for visit in visits:
                self.visits.append(visit)

    def fetch_location(self, identifier: str) -> dict | None:
        return get_location(self.api_key, identifier)

    def load_species(self, code: str, locale: str) -> Species:
        """
        Load the species with the eBird code.

        Arguments:
            code: the eBird code for the species, e.g. 'horlar' (Horned Lark).
            locale: the locale (language) to load.

        """
        logger.info(
            "Loading species: %s, %s",
            code,
            locale,
            extra={"code": code, "locale": locale},
        )
        data = self.fetch_species(code, locale)
        return self.add_species(data)

    def load_location(self, identifier: str) -> Location:
        """
        Load the location with the given identifier.

        Arguments:
            identifier; the eBird identifier for the location, e.g. "L901738".

        """
        logger.info(
            "Loading location: %s", identifier, extra={"identifier": identifier}
        )
        data = self.fetch_location(identifier)
        return self.add_location(data)

    def load_checklist(self, identifier: str) -> Checklist:
        """
        Load the checklist with the given identifier.

        IMPORTANT: If the Location does not exist then it will be created,
        and a warning is logged. The data returned by the API  only contains
        the identifier and the state code. You can update the location record
        using the load_location() method, but this only works for hotspots.
        If the location is private then you will have to add the information
        in the Django Admin or shell.

        The Observer is also created if it does not exist. However, since the
        API only ever returns the observer's name, this is not a problem. A
        warning is still logged, in case the frequency at which this occurs
        becomes useful at some point.

        Arguments:
            identifier: the eBird identifier for the checklist, e.g. "S318722167"

        """
        logger.info(
            "Loading checklist: %s", identifier, extra={"identifier": identifier}
        )
        data = self.fetch_checklist(identifier)
        return self.add_checklist(data)

    def load_checklists(self, region: str, date: dt.date) -> None:
        """
        Load all the checklists submitted for a region for a given date.

        Arguments:
            region: The code for a national, subnational1, subnational2
                 area or hotspot identifier. For example, US, US-NY,
                 US-NY-109, or L1379126, respectively.

            date: The date the observations were made.

        """
        logger.info(
            "Loading checklists: %s, %s",
            region,
            date,
            extra={"region": region, "date": date},
        )

        try:
            self.visits = []
            self.checklists = []
            self.added = 0

            self.fetch_visits(region, date)

            for visit in self.visits:
                self.add_visit(visit)

            for identifier in self.checklists:
                self.load_checklist(identifier)

            logger.info(
                "Loading succeeded: %s, %s",
                region,
                date,
                extra={
                    "region": region,
                    "date": date,
                    "visits": len(self.visits),
                    "added": self.added,
                },
            )

        except (URLError, HTTPError):
            logger.exception(
                "Loading failed: %s, %s",
                region,
                date,
                extra={
                    "region": region,
                    "date": date,
                },
            )

    def update_checklist(self, identifier: str) -> Checklist:
        """
        Update the checklist with the given identifier.

        Arguments:
            identifier: the eBird identifier for the checklist, e.g. "S318722167"

        """
        logger.info(
            "Updating checklist: %s", identifier, extra={"identifier": identifier}
        )
        data = self.fetch_checklist(identifier)
        return self.add_checklist(data)

    def update_checklists(self, date: dt.date):
        """
        Update all the checklists for a given date.

        Arguments:
            date: The checklist date.

        """
        logger.info("Updating checklists: %s", date, extra={"date": date})

        try:
            identifiers = Checklist.objects.filter(date=date).values_list(
                "identifier", flat=True
            )
            for identifier in identifiers:
                self.update_checklist(identifier)
        except (URLError, HTTPError):
            logger.exception(
                "Updating failed: %s",
                date,
                extra={
                    "date": date,
                },
            )
