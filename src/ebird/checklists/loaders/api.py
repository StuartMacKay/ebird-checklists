import datetime as dt
import decimal
import logging
import re
from typing import Any, Optional  # TODO is this still needed? Only for < python 3.10
from urllib.error import HTTPError, URLError

from ebird.api import get_checklist, get_regions, get_visits

from .utils import str2date, str2datetime, str2int, str2decimal
from ..models import Checklist, Location, Observation, Observer, Species

logger = logging.getLogger(__name__)


class APILoader:
    """
    The APILoader downloads checklists from the eBird API and saves
    them to the database.

    """

    def __init__(self, api_key: str, force_update: bool = False):
        self.api_key: str = api_key
        self.force_update = force_update
        self.locations = {}

    def fetch_visits(self, region: str, date: dt.date = None) -> list:
        data: list = get_visits(self.api_key, region, date=date, max_results=200)
        num_visits = len(data)
        logger.info(
            "Checklists submitted: %d",
            num_visits,
            extra={"number_of_visits": num_visits},
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
                "Loading sub-regions",
                extra={"sub_regions": sub_regions},
            )
        else:
            sub_regions = []
            logger.warning(
                "Result limit exceeded: %s",
                region,
                extra={"region": region, "region_type": region_type},
            )

        return sub_regions

    def fetch_checklist(self, identifier: str) -> dict[str, Any]:
        data = get_checklist(self.api_key, identifier)
        logger.info(
            "Loading checklist: %s",
            identifier,
            extra={"identifier": identifier},
        )
        return data

    @staticmethod
    def get_urn(row: dict[str, str]) -> str:
        return f"URN:CornellLabOfOrnithology:{row['projId']}:{row['obsId']}"

    def load_location(self, identifier: str) -> Location:
        if identifier in self.locations:
            data = self.locations[identifier]
        else:
            visits = get_visits(self.api_key, identifier, max_results=1)
            data = visits[0]["loc"]

        values: dict[str, Any] = {
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

    @staticmethod
    def get_observer(data: dict[str, Any]) -> Observer:
        name: str = data["userDisplayName"]
        timestamp: dt.datetime = dt.datetime.now()
        observer: Observer

        values: dict[str, Any] = {
            "identifier": "",
            "name": name,
        }

        if observer := Observer.objects.filter(name=name).first():
            for key, value in values.items():
                setattr(observer, key, value)
            observer.save()
        else:
            observer = Observer.objects.create(**values)
        return observer

    @staticmethod
    def get_species(data: dict[str, Any]) -> Species:
        code = data["speciesCode"]
        species, created = Species.objects.get_or_create(species_code=code)
        if created:
            logger.warning(
                "Species added: %s",
                code,
                extra={"species_code": code},
            )
        return species

    def get_observation(
        self, data: dict[str, Any], checklist: Checklist
    ) -> Observation:
        identifier: str = data["obsId"]
        count: Optional[int]
        observation: Observation

        if re.match(r"\d+", data["howManyStr"]):
            count = str2int(data["howManyStr"])
            if count == 0:
                count = None
        else:
            count = None

        values: dict[str, Any] = {
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

    def load_checklist(self, identifier: str) -> Checklist:
        data = self.fetch_checklist(identifier)

        created: dt.datetime = str2datetime(data["creationDt"])
        edited: dt.datetime = str2datetime(data["lastEditedDt"])

        time: Optional[dt.time] = None
        if data["obsTimeValid"]:
            time_str: str = data["obsDt"].split(" ", 1)[1]
            time = dt.datetime.strptime(time_str, "%H:%M").time()

        duration: Optional[str] = None
        if "durationHrs" in data:
            duration = str2int(data["durationHrs"] * 60.0)

        values = {
            "created": created,
            "edited": edited,
            "identifier": identifier,
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

        new = False
        modified = False

        if checklist := Checklist.objects.filter(identifier=identifier).first():
            if self.force_update or checklist.edited < edited:
                values["location"] = self.load_location(data["locId"])
                values["observer"] = self.get_observer(data)
                for key, value in values.items():
                    setattr(checklist, key, value)
                checklist.save()
                modified = True
        else:
            values["location"] = self.load_location(data["locId"])
            values["observer"] = self.get_observer(data)
            checklist = Checklist.objects.create(**values)
            new = True

        if new or modified:
            for observation_data in data["obs"]:
                self.get_observation(observation_data, checklist)

        if modified:
            logger.info(
                "Checklist updated: %s",
                identifier,
                extra={"identifier": identifier},
            )

            queryset = checklist.observations.filter(edited__lt=edited)

            if queryset.exists():
                count, deletions = queryset.delete()
                logger.info(
                    "Orphaned observations deleted: %d",
                    count,
                    extra={"number_deleted": count},
                )

        return checklist

    def load_checklists(self, region: str, date: dt.date) -> None:
        """
        Load all the checklists submitted for a region for a given date.

        :param region: The code for a national, subnational1, subnational2
                       area or hotspot identifier. For example, US, US-NY,
                       US-NY-109, or L1379126, respectively.

        :param date: The date the observations were made.

        """
        logger.info(
            "Loading checklists: %s, %s",
            region,
            date,
            extra={"region": region, "date": date},
        )

        try:
            visits = self.fetch_visits(region, date)

            if len(visits) == 200:
                logger.warning("Max results exceeded: %s", region)

                for sub_region in self.fetch_subregions(region):
                    self.load_checklists(sub_region, date)
            else:
                self.locations = {}
                for visit in visits:
                    self.locations[visit["locId"]] = visit["loc"]
                    self.load_checklist(visit["subId"])

            logger.info("Loading succeeded")

        except (URLError, HTTPError):
            logger.exception("Loading failed")
