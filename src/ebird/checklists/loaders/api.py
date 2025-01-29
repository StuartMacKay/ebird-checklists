import datetime as dt
import decimal
import logging
import re
from urllib.error import HTTPError, URLError

from ebird.api import get_checklist, get_hotspot, get_regions, get_visits

from .utils import str2date, str2datetime, float2int, str2decimal
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

        force_update: always update the checklist database, even if the edited
            date has not changed. This is used to fix the data when a bug is
            discovered. You should not need this.

    The eBird API limits the number of records returned to 200. When downloading
    the visits for a given region if 200 hundred records are returned then it is
    assumed there are more and the loader will fetch the sub-regions and download
    the visits for each, repeating the process if necessary. To give an extreme
    example if you download the visits for the United State, "US" then the API
    will always return 200 results and the loader then download the visits to
    each of the 50 states and then each of the 3143 counties. DON'T DO THIS.
    Even if you don't get banned, karma will ensure bad things happen to you.

    """

    def __init__(self, api_key: str, force_update: bool = False):
        self.api_key: str = api_key
        self.force_update = force_update
        self.visits: list = []
        self.checklists: list = []
        self.added: int = 0
        self.updated: int = 0
        self.unchanged: int = 0

    def add_checklist(self, data: dict) -> Checklist:
        identifier = data["subId"]
        created: dt.datetime = str2datetime(data["creationDt"])
        edited: dt.datetime = str2datetime(data["lastEditedDt"])

        time: dt.time | None = None
        if data["obsTimeValid"]:
            time_str: str = data["obsDt"].split(" ", 1)[1]
            time = dt.datetime.strptime(time_str, "%H:%M").time()

        duration: str | None = None
        if "durationHrs" in data:
            duration = float2int(data["durationHrs"] * 60.0)

        values = {
            "created": created,
            "edited": edited,
            "identifier": identifier,
            "location": self.get_location(data),
            "observer": self.get_observer(data),
            "group": "",
            "species_count": data["numSpecies"],
            "date": str2date(data["obsDt"]),
            "time": time,
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

        added: bool = False
        modified: bool = False

        if checklist := Checklist.objects.filter(identifier=identifier).first():
            if checklist.edited is None:
                for key, value in values.items():
                    setattr(checklist, key, value)
                modified = True
                self.added += 1
            elif checklist.edited < edited:
                for key, value in values.items():
                    setattr(checklist, key, value)
                modified = True
                self.updated += 1
            elif self.force_update:
                for key, value in values.items():
                    setattr(checklist, key, value)
                modified = True
            else:
                self.unchanged += 1

            if modified:
                checklist.save()
                logger.info(
                    "Checklist updated: %s",
                    identifier,
                    extra={"identifier": identifier},
                )
            else:
                logger.info(
                    "Checklist unchanged: %s",
                    identifier,
                    extra={"identifier": identifier},
                )
        else:
            checklist = Checklist.objects.create(**values)
            added = True
            self.added += 1
            logger.info(
                "Checklist added: %s",
                identifier,
                extra={"identifier": identifier},
            )

        if added or modified:
            for observation_data in data["obs"]:
                self.add_observation(observation_data, checklist)

        if modified:
            queryset = checklist.observations.filter(edited__lt=edited)

            if queryset.exists():
                count, deletions = queryset.delete()
                logger.info(
                    "Orphaned observations deleted: %d",
                    count,
                    extra={"number_deleted": count},
                )

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

    def add_visit(self, data: dict) -> Checklist:
        identifier = data["subId"]

        date: dt.date = dt.datetime.strptime(data["obsDt"], "%d %b %Y").date()
        time: dt.time | None = None

        if "obsTime" in data:
            time = dt.datetime.strptime(data["obsTime"], "%H:%M").time()

        values = {
            "location": self.add_location(data["loc"]),
            "observer": self.add_observer(data),
            "group": "",
            "species_count": data["numSpecies"],
            "date": date,
            "time": time,
            "protocol": "",
            "protocol_code": "",
            "project_code": "",
            "comments": "",
            "url": "https://ebird.org/checklist/%s" % identifier,
        }

        if checklist := Checklist.objects.filter(identifier=identifier).first():
            modified: bool = False

            for attr in ["date", "time", "species_count"]:
                if getattr(checklist, attr) != values[attr]:
                    modified = True

            if checklist.location_id != values["location"].id:
                modified = True
            if checklist.observer_id != values["observer"].id:
                modified = True

            if modified:
                for key, value in values.items():
                    setattr(checklist, key, value)
                checklist.save()
                logger.info(
                    "Visit updated: %s",
                    identifier,
                    extra={"identifier": identifier},
                )
        else:
            checklist = Checklist.objects.create(identifier=identifier, **values)
            logger.info(
                "Visit added: %s",
                identifier,
                extra={"identifier": identifier},
            )

        self.checklists.append(identifier)

        return checklist

    @staticmethod
    def get_urn(row: dict[str, str]) -> str:
        return f"URN:CornellLabOfOrnithology:{row['projId']}:{row['obsId']}"

    @staticmethod
    def get_location(data: dict) -> Location:
        identifier: str = data["locId"]
        location = Location.objects.filter(identifier=identifier).first()
        if location is None:
            location = Location.objects.create(identifier=identifier)
            logger.warning("Location did not exist", extra={"identifier": identifier})
        return location

    @staticmethod
    def get_observer(data: dict) -> Observer:
        name: str = data["userDisplayName"]
        observer = Observer.objects.filter(name=name).first()
        if observer is None:
            observer = Observer.objects.create(name=name)
            logger.warning("Observer did not exist", extra={"observer": name})
        return observer

    @staticmethod
    def get_species(data: dict) -> Species:
        code = data["speciesCode"]
        species, created = Species.objects.get_or_create(species_code=code)
        if created:
            logger.warning(
                "Species added: %s",
                code,
                extra={"species_code": code},
            )
        return species

    def fetch_checklist(self, identifier: str) -> dict:
        data = get_checklist(self.api_key, identifier)
        logger.info(
            "Loading checklist: %s",
            identifier,
            extra={"identifier": identifier},
        )
        return data

    def fetch_subregions(self, region: str) -> list[str]:
        region_types = ["subnational1", "subnational2", None]
        levels: int = len(region.split("-", 2))
        region_type = region_types[levels - 1]

        if region_type:
            items = get_regions(self.api_key, region_type, region)
            sub_regions = [item["code"] for item in items]
            logger.warning(
                "Loading visits for sub-regions",
                extra={"region": region, "sub_regions": sub_regions},
            )
        else:
            sub_regions = []
            logger.error(
                "Region has no sub-regions: %s",
                region,
                extra={"region": region, "region_type": region_type},
            )

        return sub_regions

    def fetch_visits(self, region: str, date: dt.date = None):
        visits: list = get_visits(self.api_key, region, date=date, max_results=200)
        if (num_visits := len(visits)) == 200:
            logger.warning(
                "Visits limit exceeded: %s, %s, %d",
                region,
                date,
                num_visits,
                extra={"region": region, "date": date, "number_of_visits": num_visits},
            )

            if sub_regions := self.fetch_subregions(region):
                for sub_region in sub_regions:
                    self.fetch_visits(sub_region, date)
            else:
                # No more sub-regions, just add the 200 visits
                for visit in visits:
                    self.visits.append(visit)

        else:
            for visit in visits:
                self.visits.append(visit)
            logger.info(
                "Visits fetched: %s, %s, %d",
                region,
                date,
                num_visits,
                extra={"region": region, "date": date, "number_of_visits": num_visits},
            )

    def fetch_location(self, identifier: str) -> dict | None:
        try:
            data = get_hotspot(self.api_key, identifier)
            logger.info(
                "Location fetched: %s",
                identifier,
                extra={"identifier": identifier},
            )
        except HTTPError:
            data = None
            logger.info(
                "Location not available: %s",
                identifier,
                extra={"identifier": identifier},
            )
        return data

    def load_location(self, identifier: str) -> Location | None:
        """
        Load the location with the given identifier.

        IMPORTANT: This only works for hotpots. If the location is private
        then eBird returns a status HTTP 410 GONE, and this method returns
        None.

        Arguments:
            identifier; the eBird identifier for the location, e.g. "L901738".

        Returns:
            The Location, created or updated with the data from the API call,
            or None if the location is private.

        """
        if data := self.fetch_location(identifier):
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
            self.updated = 0
            self.unchanged = 0

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
                    "updated": self.updated,
                    "unchanged": self.unchanged,
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
