import datetime as dt
import logging
import re
from decimal import Decimal
from typing import List, Optional, Tuple
from urllib.error import HTTPError, URLError

from django.utils.timezone import get_default_timezone
from ebird.api import get_checklist, get_location, get_regions, get_visits, get_taxonomy
from ebird.api.constants import API_MAX_RESULTS

from ..models import Checklist, Location, Observation, Observer, Species

logger = logging.getLogger(__name__)


def str2datetime(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value).replace(tzinfo=get_default_timezone())


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
    example if you download the visits for the United States, "US", then the API
    will always return 200 results and the loader then download the visits to
    each of the 50 states and then each of the 3143 counties. DON'T TRY THIS
    AT HOME. Even if you don't get banned, if you melt the eBird servers, then
    karma will ensure bad things happen to you.

    """

    def __init__(self, api_key: str, locale: str):
        self.api_key: str = api_key
        self.locale: str = locale

    @staticmethod
    def is_checklist(identifier: str) -> bool:
        return Checklist.objects.filter(identifier=identifier).exists()

    def add_checklist(self, data: dict) -> Tuple[Checklist, bool]:
        identifier: str = data["subId"]
        created: dt.datetime = str2datetime(data["creationDt"])
        edited: dt.datetime = str2datetime(data["lastEditedDt"])
        started: dt.datetime = str2datetime(data["obsDt"])
        checklist: Checklist

        values: dict = {
            "created": created,
            "edited": edited,
            "location": self.get_location(data),
            "observer": self.get_observer(data),
            "observer_count": None,
            "group": "",
            "species_count": data["numSpecies"],
            "date": started.date(),
            "time": None,
            "started": started,
            "protocol": "",
            "protocol_code": data["protocolId"],
            "project_code": data["projId"],
            "duration": None,
            "complete": data["allObsReported"],
            "comments": "",
            "url": "https://ebird.org/checklist/%s" % identifier,
        }

        if data["obsTimeValid"]:
            values["time"] = started.time()

        if "numObservers" in data:
            values["observer_count"] = int(data["numObservers"])

        if duration := data.get("durationHrs"):
            values["duration"] = int(duration * 60.0)

        if data["protocolId"] == "P22":
            dist: str = data["effortDistanceKm"]
            values["distance"] = round(Decimal(dist), 3)
        elif data["protocolId"] == "P23":
            area: str = data["effortAreaHa"]
            values["area"] = round(Decimal(area), 3)

        if "comments" in data:
            values["comments"] = data["comments"]

        added: bool = False

        if checklist := Checklist.objects.filter(identifier=identifier).first():
            for key, value in values.items():
                setattr(checklist, key, value)
            checklist.save()
        else:
            checklist = Checklist.objects.create(identifier=identifier, **values)
            added = True

        for observation_data in data["obs"]:
            self.add_observation(observation_data, checklist)

        for observation in checklist.observations.filter(edited__lt=edited):  # pyright: ignore [reportAttributeAccessIssue]
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

        return checklist, added

    @staticmethod
    def add_location(data: dict) -> Location:
        identifier: str = data["locId"]
        location: Location

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
            "latitude": Decimal(data["latitude"]),
            "longitude": Decimal(data["longitude"]),
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
        observation: Observation

        values: dict = {
            "edited": checklist.edited,
            "identifier": identifier,
            "checklist": checklist,
            "location": checklist.location,
            "observer": checklist.observer,
            "species": self.get_species(data),
            "count": None,
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

        if re.match(r"\d+", data["howManyStr"]):
            values["count"] = int(data["howManyStr"]) or None

        if "comments" in data:
            values["comments"] = data["comments"]

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
        observer, _ = Observer.objects.get_or_create(name=name)
        return observer

    @staticmethod
    def add_species(data: dict) -> Species:
        code: str = data["speciesCode"]
        species: Species

        values: dict = {
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
                setattr(species, key, value)
            species.save()
        else:
            species = Species.objects.create(species_code=code, **values)

        return species

    @staticmethod
    def get_urn(row: dict) -> str:
        return f"URN:CornellLabOfOrnithology:{row['projId']}:{row['obsId']}"

    def get_location(self, data: dict) -> Location:
        identifier: str = data["locId"]
        location: Location = Location.objects.filter(identifier=identifier).first()
        if location is None:
            location = self.load_location(identifier)
        return location

    @staticmethod
    def get_observer(data: dict) -> Observer:
        name: str = data["userDisplayName"]
        observer: Observer = Observer.objects.filter(name=name).first()
        if observer is None:
            observer = Observer.objects.create(name=name)
        return observer

    def get_species(self, data: dict) -> Species:
        code: str = data["speciesCode"]
        species: Species
        if (species := Species.objects.filter(species_code=code).first()) is None:
            species = self.load_species(code, self.locale)
        return species

    def fetch_checklist(self, identifier: str) -> dict:
        data: dict = get_checklist(self.api_key, identifier)
        return data

    def fetch_species(self, code: str, locale: str) -> dict:
        return get_taxonomy(self.api_key, locale=locale, species=code)[0]

    def fetch_subregions(self, region: str) -> List[str]:
        logger.info(
            "Fetching sub-regions: %s",
            region,
            extra={"region": region},
        )
        region_types: list = ["subnational1", "subnational2", None]
        levels: int = len(region.split("-", 2))
        region_type: Optional[str] = region_types[levels - 1]

        if region_type:
            items: list = get_regions(self.api_key, region_type, region)
            sub_regions = [item["code"] for item in items]
        else:
            sub_regions = []

        return sub_regions

    def fetch_visits(self, region: str, date: Optional[dt.date] = None):
        visits = []

        results: list = get_visits(
            self.api_key, region, date=date, max_results=API_MAX_RESULTS
        )

        if len(results) == API_MAX_RESULTS:
            if sub_regions := self.fetch_subregions(region):
                for sub_region in sub_regions:
                    logger.info(
                        "Loading checklists for sub-regions: %s, %s",
                        sub_region,
                        date,
                        extra={"region": sub_region, "date": date},
                    )
                    visits.extend(self.fetch_visits(sub_region, date))
            else:
                # No more sub-regions, issue a warning and return the results
                visits.extend(results)
                logger.warning(
                    "Loading checklists - API limit reached: %s, %s",
                    region,
                    date,
                    extra={"region": region, "date": date},
                )
        else:
            visits.extend(results)

        return visits

    def fetch_location(self, identifier: str) -> dict:
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
        data: dict = self.fetch_species(code, locale)
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
        data: dict = self.fetch_location(identifier)
        return self.add_location(data)

    def load_checklist(self, identifier: str) -> Tuple[Checklist, bool]:
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
        data: dict = self.fetch_checklist(identifier)
        return self.add_checklist(data)

    def load_checklists(self, region: str, date: dt.date, new_only: bool) -> None:
        """
        Load all the checklists submitted for a region for a given date.

        Arguments:
            region: The code for a national, subnational1, subnational2
                 area or hotspot identifier. For example, US, US-NY,
                 US-NY-109, or L1379126, respectively.

            date: The date the observations were made.

            new_only: If true, Load only new checklists, otherwise load all.

        """
        scope = "new" if new_only else "all"

        logger.info(
            "Loading %s checklists: %s, %s",
            scope,
            region,
            date,
            extra={"region": region, "date": date, "scope": scope},
        )
        visits: list[dict]
        number_of_visits: int = 0
        locations: dict = {}
        checklists: List[str] = []
        added: int = 0
        loaded: int = 0

        try:
            visits = self.fetch_visits(region, date)
            number_of_visits = len(visits)

            for visit in visits:
                location = visit["loc"]
                identifier = location["locId"]
                locations[identifier] = location

            if new_only:
                for visit in visits:
                    identifier = visit["subId"]
                    if not self.is_checklist(identifier):
                        checklists.append(identifier)
            else:
                for visit in visits:
                    identifier = visit["subId"]
                    checklists.append(identifier)

            for data in locations.values():
                self.add_location(data)

            for identifier in checklists:
                _, created = self.load_checklist(identifier)
                if created:
                    added += 1
                loaded += 1

            logger.info(
                "Loading %s checklists succeeded: %s, %s",
                scope,
                region,
                date,
                extra={
                    "region": region,
                    "date": date,
                    "scope": scope,
                    "visits": number_of_visits,
                    "added": added,
                    "loaded": loaded,
                },
            )

        except (URLError, HTTPError):
            logger.exception(
                "Loading %s checklists failed: %s, %s",
                scope,
                region,
                date,
                extra={
                    "region": region,
                    "date": date,
                    "scope": scope,
                    "visits": number_of_visits,
                    "added": added,
                    "loaded": loaded,
                },
            )

    def load_recent(self, days: int, region: str, new: bool):
        today: dt.date = dt.date.today()
        dates: list[dt.date] = [today - dt.timedelta(days=n) for n in range(days)]
        for date in dates:
            self.load_checklists(region, date, new)
