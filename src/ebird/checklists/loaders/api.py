import datetime as dt
import logging
import re
from typing import Any, Optional
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

    def __init__(self, api_key: str):
        self.api_key: str = api_key

    def get_visits(self, region: str, date: dt.date = None) -> list:
        data: list = get_visits(self.api_key, region, date=date, max_results=200)
        num_visits = len(data)
        logger.info(
            "eBird API: checklists submitted: %d",
            num_visits,
            extra={"number_of_visits": num_visits},
        )
        return data

    def get_subregions(self, region: str) -> list[str]:
        region_types = ["subnational1", "subnational2", None]
        levels: int = len(region.split("-", 2))
        region_type = region_types[levels - 1]

        if region_type:
            items = get_regions(self.api_key, region_type, region)
            sub_regions = [item["code"] for item in items]
            logger.warning(
                "eBird API: loading sub-regions",
                extra={"sub_regions": sub_regions},
            )
        else:
            sub_regions = []
            logger.warning(
                "eBird API: result limit exceeded: %s",
                region,
                extra={"region": region, "region_type": region_type},
            )

        return sub_regions

    def get_checklist(self, identifier: str) -> dict[str, Any]:
        data = get_checklist(self.api_key, identifier)
        logger.info(
            "eBird API: loading checklist: %s",
            identifier,
            extra={"identifier": identifier},
        )
        return data

    @staticmethod
    def get_observation_global_identifier(row: dict[str, str]) -> str:
        return f"URN:CornellLabOfOrnithology:{row['projId']}:{row['obsId']}"

    @staticmethod
    def create_or_update_location(data: dict[str, Any]) -> Location:
        identifier: str = data["locId"]

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
    def create_or_update_observer(data: dict[str, Any]) -> Observer:
        # The observer's name is used as the unique identifier, even
        # though it is not necessarily unique. However this works until
        # better solution is found.
        name: str = data["userDisplayName"]
        timestamp: dt.datetime = dt.datetime.now()
        observer: Observer

        values: dict[str, Any] = {
            "modified": timestamp,
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
                "eBird API: species added: %s",
                code,
                extra={"species_code": code},
            )
        return species

    def create_or_update_observation(
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
            "urn": self.get_observation_global_identifier(data),
        }

        if observation := Observation.objects.filter(identifier=identifier).first():
            if observation.edited < checklist.edited:
                for key, value in values.items():
                    setattr(observation, key, value)
                observation.save()
        else:
            observation = Observation.objects.create(**values)
        return observation

    def create_or_update_checklist(self, visit: dict[str, Any]) -> Checklist:
        identifier: str = visit["subId"]

        data = self.get_checklist(identifier)

        edited: dt.datetime = str2datetime(data["lastEditedDt"])

        time: Optional[dt.time] = None
        if data["obsTimeValid"]:
            time_str: str = data["obsDt"].split(" ", 1)[1]
            time = dt.datetime.strptime(time_str, "%H:%M").time()

        duration: Optional[str] = None
        if "durationHrs" in data:
            duration = str2int(data["durationHrs"] * 60.0)

        values = {
            "identifier": identifier,
            "edited": edited,
            "observer_count": str2int(data.get("numObservers")),
            "group": "",
            "species_count": data["numSpecies"],
            "date": str2date(data["obsDt"]),
            "time": time,
            "protocol": "",
            "protocol_code": data["protocolId"],
            "project_code": data["projId"],
            "duration": duration,
            "distance": str2decimal(data.get("distKm")),
            "area": str2decimal(data.get("areaHa")),
            "complete": data.get("allObsReported", False),
            "comments": "",
            "url": "https://ebird.org/checklist/%s" % identifier,
        }

        modified = False

        if checklist := Checklist.objects.filter(identifier=identifier).first():
            if checklist.edited < edited:
                values["location"] = self.create_or_update_location(visit["loc"])
                values["observer"] = self.create_or_update_observer(visit)
                for key, value in values.items():
                    setattr(checklist, key, value)
                checklist.save()
                modified = True
        else:
            values["location"] = self.create_or_update_location(visit["loc"])
            values["observer"] = self.create_or_update_observer(visit)
            checklist = Checklist.objects.create(**values)

        for observation_data in data["obs"]:
            self.create_or_update_observation(observation_data, checklist)

        if modified:
            logger.info(
                "eBird API: checklist updated: %s",
                identifier,
                extra={"identifier": identifier},
            )

            queryset = checklist.observations.filter(edited__lt=edited)

            if count := queryset.count():
                checklist.observations.filter(edited__lt=edited).delete()
                logger.info(
                    "eBird API: orphaned observations deleted: %d",
                    count,
                    extra={"number_deleted": count},
                )

        return checklist

    def load(self, region: str, date: dt.date) -> None:
        """
        Load all the checklists submitted for a region for a given date.

        :param region: The code for a national, subnational1, subnational2
                       area or hotspot identifier. For example, US, US-NY,
                       US-NY-109, or L1379126, respectively.

        :param date: The date the observations were made.

        """
        logger.info(
            "eBird API: loading checklists: %s, %s",
            region,
            date,
            extra={"region": region, "date": date},
        )

        try:
            visits = self.get_visits(region, date)

            if len(visits) == 200:
                logger.warning("eBird API: result limit exceeded: %s", region)

                for sub_region in self.get_subregions(region):
                    self.load(sub_region, date)
            else:
                for visit in visits:
                    self.create_or_update_checklist(visit)

            logger.info("eBird API: loading succeeded")

        except (URLError, HTTPError):
            logger.exception("eBird API: loading failed")
