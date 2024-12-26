import csv
import datetime as dt
import logging
import re
from pathlib import Path
from typing import Any, Optional

from ..models import Checklist, Location, Observation, Observer, Species
from .utils import str2int, str2decimal, update_object

logger = logging.getLogger(__name__)


class MyDataLoader:

    @staticmethod
    def _get_location(data: dict[str, Any]) -> Location:
        identifier: str = data["Location ID"]

        values: dict[str, Any] = {
            "identifier": identifier,
            "type": "",
            "name": data["Location"],
            "county": data["County"],
            "county_code": "",
            "state": data["State/Province"],
            "state_code": "",
            "country": "",
            "country_code": data["County"].split("-")[0],
            "iba_code": "",
            "bcr_code": "",
            "usfws_code": "",
            "atlas_block": "",
            "latitude": str2decimal(data["Latitude"]),
            "longitude": str2decimal(data["Longitude"]),
            "url": "https://ebird.org/region/%s" % identifier,
        }

        if obj := Location.objects.filter(identifier=identifier).first():
            location = update_object(obj, values)
        else:
            location = Location.objects.create(**values)

        return location

    @staticmethod
    def _get_observer(name: str) -> Observer:
        timestamp: dt.datetime = dt.datetime.now()
        observer: Observer

        values = {"modified": timestamp, "identifier": "", "name": name}

        if obj := Observer.objects.filter(name=name).first():
            observer = update_object(obj, values)
        else:
            observer = Observer.objects.create(**values)

        return observer

    @staticmethod
    def _get_species(data: dict[str, Any]) -> Species:
        order = data["Taxonomic Order"]
        species: Species

        values: dict[str, Any] = {
            "taxon_order": order,
            "order": "",
            "category": "",
            "species_code": "",
            "family_code": "",
            "common_name": data["Common Name"],
            "scientific_name": data["Scientific Name"],
            "family_common_name": "",
            "family_scientific_name": "",
            "subspecies_common_name": "",
            "subspecies_scientific_name": "",
            "exotic_code": "",
        }

        if obj := Species.objects.filter(order=order).first():
            species = update_object(obj, values)
        else:
            species = Species.objects.create(**values)

        return species

    def _get_observation(
        self, data: dict[str, Any], checklist: Checklist
    ) -> Observation:
        count: Optional[int]

        if re.match(r"\d+", data["Count"]):
            count = str2int(data["Count"])
            if count == 0:
                count = None
        else:
            count = None

        values: dict[str, Any] = {
            "edited": checklist.edited,
            "identifier": "",
            "species": self._get_species(data),
            "checklist": checklist,
            "location": checklist.location,
            "observer": checklist.observer,
            "count": count,
            "breeding_code": data["Breeding Code"] or "",
            "breeding_category": "",
            "behavior_code": "",
            "age_sex": "",
            "media": len(data["ML Catalog Num`bers"] or "") > 0,
            "approved": None,
            "reviewed": None,
            "reason": "",
            "comments": data["Observation Details"] or "",
            "urn": "",
        }

        # There is no unique identifier for an observation, only the
        # count, species, date, time, checklist identifier and location
        # serve to identify it. If any of these change then the original
        # observation cannot be retrieved, so updating records is not
        # practical / possible. It only makes sense to add the record each
        # time the data is loaded. Unless the data is cleared that will
        # result in duplicate records being created.
        return Observation.objects.create(**values)

    @staticmethod
    def _get_checklist(
        data: dict[str, Any], location: Location, observer: Observer
    ) -> Checklist:
        identifier: str = data["Submission ID"]
        time: Optional[dt.time]

        if value := data["Time"]:
            time = dt.datetime.strptime(value, "%H:%M %p").time()
        else:
            time = None

        values: dict[str, Any] = {
            "identifier": identifier,
            "location": location,
            "observer": observer,
            "observer_count": str2int(data["Number of Observers"]),
            "group": "",
            "species_count": None,
            "date": dt.datetime.strptime(data["Date"], "%Y-%m-%d").date(),
            "time": time,
            "protocol": data["Protocol"],
            "protocol_code": "",
            "project_code": "",
            "duration": str2int(data["Duration (Min)"]),
            "distance": str2decimal(data["Distance Traveled (km)"]),
            "area": str2decimal(data["Area Covered (ha)"]),
            "complete": data["All Obs Reported"] == "1",
            "comments": data["Checklist Comments"] or "",
            "url": "https://ebird.org/checklist/%s" % identifier,
        }

        if obj := Checklist.objects.filter(identifier=identifier).first():
            checklist = update_object(obj, values)
        else:
            checklist = Checklist.objects.create(**values)

        return checklist

    def load(self, path: Path, observer_name: str) -> None:
        if not path.exists():
            raise IOError('File "%s" does not exist' % path)

        logger.info("Loading My eBird Data", extra={"path": path})

        with open(path) as csvfile:
            loaded: int = 0
            reader = csv.DictReader(csvfile, delimiter=",")
            observer: Observer = self._get_observer(observer_name)
            for data in reader:
                location: Location = self._get_location(data)
                checklist: Checklist = self._get_checklist(data, location, observer)
                self._get_observation(data, checklist)
                loaded += 1

        logger.info("Loaded My eBird Data", extra={"loaded": loaded})
