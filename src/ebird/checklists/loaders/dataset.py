import csv
import datetime as dt
import logging
import re
from pathlib import Path
from typing import Any, Optional

from django.utils.timezone import get_default_timezone

from ..models import Checklist, Location, Observation, Observer, Species
from .utils import str2bool, str2int, str2decimal, update_object

logger = logging.getLogger(__name__)


class BasicDatasetLoader:
    @staticmethod
    def _get_observation_status(identifier: str, last_edited: str) -> tuple[bool, bool]:
        last_edited_date: dt.datetime = dt.datetime.fromisoformat(last_edited).replace(
            tzinfo=get_default_timezone()
        )
        new: bool
        modified: bool

        if obj := Observation.objects.filter(identifier=identifier).first():
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

    @staticmethod
    def _get_location(data: dict[str, str]) -> Location:
        identifier: str = data["LOCALITY ID"]

        values: dict[str, Any] = {
            "identifier": identifier,
            "type": data["LOCALITY TYPE"],
            "name": data["LOCALITY"],
            "county": data["COUNTY"],
            "county_code": data["COUNTY CODE"],
            "state": data["STATE"],
            "state_code": data["STATE CODE"],
            "country": data["COUNTRY"],
            "country_code": data["COUNTRY CODE"],
            "latitude": str2decimal(data["LATITUDE"]),
            "longitude": str2decimal(data["LONGITUDE"]),
            "iba_code": data["IBA CODE"],
            "bcr_code": data["BCR CODE"],
            "usfws_code": data["USFWS CODE"],
            "atlas_block": data["ATLAS BLOCK"],
            "url": "https://ebird.org/region/%s" % identifier,
        }

        if obj := Location.objects.filter(identifier=identifier).first():
            location = update_object(obj, values)
        else:
            location = Location.objects.create(**values)
        return location

    @staticmethod
    def _get_observer(data: dict[str, str]) -> Observer:
        identifier: str = data["OBSERVER ID"]

        values: dict[str, Any] = {
            "identifier": identifier,
            "name": "",
        }

        if obj := Observer.objects.filter(identifier=identifier).first():
            observer = update_object(obj, values)
        else:
            observer = Observer.objects.create(**values)
        return observer

    @staticmethod
    def _get_species(data: dict[str, str]) -> Species:
        taxon_order = data["TAXONOMIC ORDER"]
        species: Species

        values: dict[str, Any] = {
            "taxon_order": taxon_order,
            "order": "",
            "category": data["CATEGORY"],
            "species_code": "",
            "family_code": "",
            "common_name": data["COMMON NAME"],
            "scientific_name": data["SCIENTIFIC NAME"],
            "family_common_name": "",
            "family_scientific_name": "",
            "subspecies_common_name": data["SUBSPECIES COMMON NAME"],
            "subspecies_scientific_name": data["SUBSPECIES SCIENTIFIC NAME"],
            "exotic_code": data["EXOTIC CODE"],
        }

        if obj := Species.objects.filter(taxon_order=taxon_order).first():
            species = update_object(obj, values)
        else:
            species = Species.objects.create(**values)
        return species

    @staticmethod
    def _get_observation(
        data: dict[str, str], checklist: Checklist, species: Species
    ) -> Observation:
        identifier = data["GLOBAL UNIQUE IDENTIFIER"].split(":")[-1]
        count: Optional[int]
        observation: Observation

        if re.match(r"\d+", data["OBSERVATION COUNT"]):
            count = str2int(data["OBSERVATION COUNT"])
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
            "species": species,
            "count": count,
            "breeding_code": data["BREEDING CODE"],
            "breeding_category": data["BREEDING CATEGORY"],
            "behavior_code": data["BEHAVIOR CODE"],
            "age_sex": data["AGE/SEX"],
            "media": str2bool(data["HAS MEDIA"]),
            "approved": str2bool(data["APPROVED"]),
            "reviewed": str2bool(data["REVIEWED"]),
            "reason": data["REASON"] or "",
            "comments": data["SPECIES COMMENTS"] or "",
            "urn": data["GLOBAL UNIQUE IDENTIFIER"],
        }

        if obj := Observation.objects.filter(identifier=identifier).first():
            observation = update_object(obj, values)
        else:
            observation = Observation.objects.create(**values)

        return observation

    @staticmethod
    def _get_checklist(
        row: dict[str, str],
        location: Location,
        observer: Observer,
    ) -> Checklist:
        identifier: str = row["SAMPLING EVENT IDENTIFIER"]
        edited: dt.datetime = dt.datetime.fromisoformat(
            row["LAST EDITED DATE"]
        ).replace(tzinfo=get_default_timezone())
        time: Optional[dt.time]

        if value := row["TIME OBSERVATIONS STARTED"]:
            time = dt.datetime.strptime(value, "%H:%M:%S").time()
        else:
            time = None

        values: dict[str, Any] = {
            "identifier": identifier,
            "edited": edited,
            "location": location,
            "observer": observer,
            "group": row["GROUP IDENTIFIER"],
            "observer_count": row["NUMBER OBSERVERS"],
            "date": dt.datetime.strptime(row["OBSERVATION DATE"], "%Y-%m-%d").date(),
            "time": time,
            "protocol": row["PROTOCOL TYPE"],
            "protocol_code": row["PROTOCOL CODE"],
            "project_code": row["PROJECT CODE"],
            "duration": str2int(row["DURATION MINUTES"]),
            "distance": str2decimal(row["EFFORT DISTANCE KM"]),
            "area": str2decimal(row["EFFORT AREA HA"]),
            "complete": str2bool(row["ALL SPECIES REPORTED"]),
            "comments": row["TRIP COMMENTS"] or "",
            "url": "https://ebird.org/checklist/%s" % identifier,
        }

        if obj := Checklist.objects.filter(identifier=identifier).first():
            checklist = update_object(obj, values)
        else:
            checklist = Checklist.objects.create(**values)

        return checklist

    def load(self, path: Path) -> None:
        if not path.exists():
            raise IOError('File "%s" does not exist' % path)

        added: int = 0
        updated: int = 0
        unchanged: int = 0
        loaded: int = 0

        logger.info("Loading eBird Basic Dataset", extra={"path": path})

        with open(path) as csvfile:
            new: bool
            modified: bool

            reader = csv.DictReader(csvfile, delimiter="\t")
            for row in reader:
                identifier: str = row["GLOBAL UNIQUE IDENTIFIER"]
                last_edited: str = row["LAST EDITED DATE"]

                new, modified = self._get_observation_status(identifier, last_edited)

                if new or modified:
                    location: Location = self._get_location(row)
                    observer: Observer = self._get_observer(row)
                    checklist: Checklist = self._get_checklist(row, location, observer)
                    species: Species = self._get_species(row)
                    self._get_observation(row, checklist, species)

                if new:
                    added += 1
                elif modified:
                    updated += 1
                else:
                    unchanged += 1

                loaded += 1

        logger.info(
            "Loaded eBird Basic Dataset",
            extra={
                "loaded": loaded,
                "added": added,
                "updated": updated,
                "unchanged": unchanged,
            },
        )
