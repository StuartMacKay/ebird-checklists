import datetime as dt
import logging
import re
from typing import Any, Optional
from urllib.error import HTTPError, URLError

from django.utils.timezone import get_default_timezone
from ebird.api import get_checklist, get_visits

from ..models import Checklist, Location, Observation, Observer, Species
from .utils import str2int, str2decimal, update_object

logger = logging.getLogger(__name__)


class APILoader:
    """
    The APILoader downloads checklists from the eBird API and saves
    them to the database.

    """

    def __init__(self, api_key: str):
        self.api_key: str = api_key

    @staticmethod
    def _get_checklist_status(identifier: str, last_edited: str) -> tuple[bool, bool]:
        last_edited_date: dt.datetime = dt.datetime.fromisoformat(last_edited).replace(
            tzinfo=get_default_timezone()
        )
        new: bool
        modified: bool

        if obj := Checklist.objects.filter(identifier=identifier).first():
            if obj.edited < last_edited_date:
                new = False
                modified = True
            else:
                new = False
                modified = False
        else:
            new = True
            modified = False
        return new, modified

    def _fetch_visits(self, region: str, date: dt.date) -> list:
        visits: list

        logger.info("Fetching visits", extra={"region": region, "date": date})

        try:
            visits = get_visits(self.api_key, region, date=date, max_results=200)
            logger.info("Visits fetched", extra={"number_of_visits": len(visits)})
        except (URLError, HTTPError):
            logger.exception("Visits not fetched")
            raise

        return visits

    def _fetch_recent(self, region: str, limit: int = 200) -> list:
        visits: list

        logger.info("Fetching recent visits", extra={"region": region, "limit": limit})

        try:
            visits = get_visits(self.api_key, region, max_results=limit)
        except (URLError, HTTPError):
            logger.exception("Recent visits not fetched")
            raise

        logger.info("Recent visits fetched", extra={"loaded": len(visits)})

        return visits

    def _fetch_checklist(self, identifier: str) -> dict[str, Any]:
        data: dict[str, Any]

        logger.info("Fetching checklist", extra={"identifier": identifier})

        try:
            data = get_checklist(self.api_key, identifier)
        except (URLError, HTTPError):
            logger.exception("Checklist not fetched")
            raise

        logger.info("Checklist fetched", extra={"identifier": identifier})

        return data

    @staticmethod
    def _get_observation_global_identifier(row: dict[str, str]) -> str:
        return f"URN:CornellLabOfOrnithology:{row['projId']}:{row['obsId']}"

    @staticmethod
    def _get_location(data: dict[str, Any]) -> Location:
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

        if obj := Location.objects.filter(identifier=identifier).first():
            location = update_object(obj, values)
        else:
            location = Location.objects.create(**values)

        return location

    @staticmethod
    def _get_observer(data: dict[str, Any]) -> Observer:
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

        if obj := Observer.objects.filter(name=name).first():
            observer = update_object(obj, values)
        else:
            observer = Observer.objects.create(**values)
        return observer

    @staticmethod
    def _get_species(data: dict[str, Any]) -> Species:
        return Species.objects.get_or_create(species_code=data["speciesCode"])[0]

    def _get_observation(
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
            "species": self._get_species(data),
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
            "urn": self._get_observation_global_identifier(data)
        }

        if obj := Observation.objects.filter(identifier=identifier).first():
            if obj.edited < checklist.edited:
                observation = update_object(obj, values)
            else:
                observation = obj
        else:
            observation = Observation.objects.create(**values)
        return observation

    @staticmethod
    def _delete_orphans(checklist: Checklist) -> None:
        # If the checklist was updated, then any observations with
        # an edited date earlier than checklist edited date must
        # have been deleted.
        for observation in checklist.observations.all():
            if observation.edited < checklist.edited:
                observation.delete()
                species = observation.species
                count = observation.count
                logger.info(
                    "Observation deleted",
                    extra={
                        "checklist": checklist.identifier,
                        "species": species,
                        "count": count,
                    },
                )

    def _get_checklist(
        self,
        data: dict[str, Any],
        location: Location,
        observer: Observer,
    ) -> Checklist:
        identifier: str = data["subId"]
        edited: dt.datetime = dt.datetime.fromisoformat(
            data["lastEditedDt"]
        ).replace(tzinfo=get_default_timezone())
        checklist: Checklist

        date_str: str = data["obsDt"].split(" ", 1)[0]
        date: dt.date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()

        time_str: str
        time: Optional[dt.time]

        if data["obsTimeValid"]:
            time_str = data["obsDt"].split(" ", 1)[1]
            time = dt.datetime.strptime(time_str, "%H:%M").time()
        else:
            time = None

        duration: Optional[str]

        if "durationHrs" in data:
            duration = data["durationHrs"] * 60.0
        else:
            duration = None

        distance: str = data.get("distKm")
        area: str = data.get("areaHa")

        values = {
            "identifier": identifier,
            "edited": edited,
            "location": location,
            "observer": observer,
            "observer_count": str2int(data.get("numObservers")),
            "group": "",
            "species_count": data["numSpecies"],
            "date": date,
            "time": time,
            "protocol": "",
            "protocol_code": data["protocolId"],
            "project_code": data["projId"],
            "duration": str2int(duration),
            "distance": str2decimal(distance),
            "area": str2decimal(area),
            "complete": data.get("allObsReported", False),
            "comments": "",
            "url": "https://ebird.org/checklist/%s" % identifier,
        }

        if obj := Checklist.objects.filter(identifier=identifier).first():
            if obj.edited < edited:
                checklist = update_object(obj, values)
            else:
                checklist = obj
        else:
            checklist = Checklist.objects.create(**values)

        for observation_data in data["obs"]:
            try:
                self._get_observation(observation_data, checklist)
            except Exception as err:  # noqa
                logger.exception(
                    "Observation not added", extra={"data": observation_data}
                )
                raise

        return checklist

    def load(self, region: str, date: dt.date) -> None:
        """
        Load all the checklists submitted for a region for a given date.

        :param region: The code for a national, subnational1, subnational2
                       area or hotspot identifier. For example, US, US-NY,
                       US-NY-109, or L1379126, respectively.

        :param date: The date the observations were made.

        """
        added: int = 0
        updated: int = 0
        unchanged: int = 0
        loaded: int

        logger.info("Loading eBird API checklists")

        for visit in self._fetch_visits(region, date):
            identifier: str = visit["subId"]
            data = self._fetch_checklist(identifier)
            last_edited: str = data["lastEditedDt"]
            new: bool
            modified: bool


            new, modified = self._get_checklist_status(identifier, last_edited)
            if new or modified:
                observer = self._get_observer(data)
                location = self._get_location(visit["loc"])
                checklist = self._get_checklist(data, location, observer)
                if modified:
                    self._delete_orphans(checklist)

            if new:
                added += 1
            elif modified:
                updated += 1
            else:
                unchanged += 1

        loaded = added + updated + unchanged

        logger.info(
            "Loaded eBird API checklists",
            extra={
                "loaded": loaded,
                "added": added,
                "updated": updated,
                "unchanged": unchanged,
            },
        )

    def recent(self, region: str, limit: int = 200) -> None:
        """
        Load the latest checklists submitted for a region.

        :param region: The code for a national, subnational1, subnational2
                       area or hotspot identifier. For example, US, US-NY,
                       US-NY-109, or L1379126, respectively.

        :param limit: The number of checklists to fetch. The default is 200,
                      which is a hard limit imposed by eBird - to avoid melting
                      the servers.
        """
        added: int = 0
        updated: int = 0
        unchanged: int = 0
        loaded: int

        logger.info("Loading eBird API recent checklists")

        for visit in self._fetch_recent(region, limit):
            identifier: str = visit["subId"]
            data = self._fetch_checklist(visit["subId"])
            last_edited: str = data["lastEditedDt"]
            new: bool
            modified: bool

            new, modified = self._get_checklist_status(identifier, last_edited)
            if new or modified:
                observer = self._get_observer(data)
                location = self._get_location(visit["loc"])
                checklist = self._get_checklist(data, location, observer)
                if modified:
                    self._delete_orphans(checklist)

            if new:
                added += 1
            elif modified:
                updated += 1
            else:
                unchanged += 1

        loaded = added + updated + unchanged

        logger.info(
            "Loaded eBird API recent checklists",
            extra={
                "loaded": loaded,
                "added": added,
                "updated": updated,
                "unchanged": unchanged,
            },
        )
