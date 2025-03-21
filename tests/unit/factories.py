# pyright: reportIncompatibleVariableOverride=false, reportPrivateImportUsage=false

import random
import string

from django.utils.timezone import get_default_timezone
from factory import Faker, LazyAttribute, SubFactory
from factory.django import DjangoModelFactory

from ebird.checklists.models import (
    Area,
    Checklist,
    Country,
    District,
    Location,
    Observation,
    Observer,
    Region,
    Species,
)

PROJECTS = [
    "EBIRD",
]

PROTOCOLS = {
    "P21": "Stationary",
    "P22": "Traveling",
}

SPECIES = {
    "Canada goose": "(Branta canadensis)",
    "Mallard": "Anas platyrhynchos",
    "Rock Pigeon (Feral Pigeon)": "Columba livia (Feral Pigeon)",
    "Common Starling": "Sturnus vulgaris",
    "House Sparrow": "Passer domesticus",
}


def random_key(values):
    return random.choice(list(values.keys()))


def random_code(length: int, prefix: str = ""):
    return prefix + "".join(random.choices(string.digits, k=length))


def random_hex_code(length: int, prefix: str = ""):
    return prefix + "".join(random.choices(string.hexdigits, k=length))


def random_lowercase(length: int, prefix: str = ""):
    return prefix + "".join(random.choices(string.ascii_lowercase, k=length))


def random_uppercase(length: int, prefix: str = ""):
    return prefix + "".join(random.choices(string.ascii_uppercase, k=length))


def random_country_code() -> str:
    return random_uppercase(2)


def random_region_code() -> str:
    country_code = random_country_code()
    return random_uppercase(2, f"{country_code}-")


def url(category: str, code: str) -> str:
    return f"https://ebird.org/{category}/{code}"


def hotspot_url(code: str) -> str:
    return url("hotspot", code)


def checklist_url(code: str) -> str:
    return url("checklist", code)


def random_district_code() -> str:
    region_code = random_region_code()
    district_code = random_uppercase(random.randint(2, 3))
    return f"{region_code}-{district_code}"


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ("code",)

    code = Faker("country_code")
    name = Faker("country")


class RegionFactory(DjangoModelFactory):
    class Meta:
        model = Region
        django_get_or_create = ("code",)

    code = LazyAttribute(lambda x: random_region_code())
    name = Faker("city")  # OK for now


class DistrictFactory(DjangoModelFactory):
    class Meta:
        model = District
        django_get_or_create = ("code",)

    code = LazyAttribute(lambda x: random_district_code())
    name = Faker("city")  # OK for now


class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location
        django_get_or_create = ("identifier",)

    identifier = LazyAttribute(lambda _: random_code(6, "L"))
    type = ""
    name = Faker("street_name")
    country = SubFactory(CountryFactory)
    region = SubFactory(RegionFactory)
    district = SubFactory(DistrictFactory)
    iba_code = ""
    bcr_code = ""
    usfws_code = ""
    atlas_block = ""
    latitude = Faker("latitude")
    longitude = Faker("longitude")
    url = LazyAttribute(lambda o: hotspot_url(o.identifier))
    hotspot = True


class ObserverFactory(DjangoModelFactory):
    class Meta:
        model = Observer
        django_get_or_create = ("name",)

    identifier = LazyAttribute(lambda _: random_code(7, "obsr"))
    name = Faker("name")


class SpeciesFactory(DjangoModelFactory):
    class Meta:
        model = Species
        django_get_or_create = ("taxon_order",)

    taxon_order = LazyAttribute(lambda _: random.randint(100000, 1000000))
    species_code = LazyAttribute(lambda _: random_lowercase(6))
    family_code = LazyAttribute(lambda _: random_lowercase(6))
    category = ""
    common_name = LazyAttribute(lambda _: random_key(SPECIES))
    scientific_name = LazyAttribute(lambda obj: SPECIES[obj.common_name])
    subspecies_common_name = ""
    subspecies_scientific_name = ""
    family_common_name = ""
    family_scientific_name = ""
    exotic_code = ""


class ChecklistFactory(DjangoModelFactory):
    class Meta:
        model = Checklist

    created = Faker("date_time", tzinfo=get_default_timezone())
    edited = Faker("date_time", tzinfo=get_default_timezone())
    identifier = LazyAttribute(lambda _: random_code(9, "S"))
    location = SubFactory(LocationFactory)
    country = LazyAttribute(lambda obj: obj.location.country)
    region = LazyAttribute(lambda obj: obj.location.region)
    district = LazyAttribute(lambda obj: obj.location.district)
    area = LazyAttribute(lambda obj: obj.location.area)
    observer = SubFactory(ObserverFactory)
    observer_count = random.randint(1, 5)
    date = Faker("date_object")
    time = Faker("time_object")
    group = ""
    protocol = LazyAttribute(lambda obj: PROTOCOLS[obj.protocol_code])
    protocol_code = LazyAttribute(lambda _: random_key(PROTOCOLS))
    project_code = LazyAttribute(lambda _: random.choice(PROJECTS))
    complete = True
    comments = ""
    url = LazyAttribute(lambda o: checklist_url(o.identifier))


class ObservationFactory(DjangoModelFactory):
    class Meta:
        model = Observation

    identifier = LazyAttribute(lambda _: random_code(10, "OBS"))
    date = LazyAttribute(lambda obj: obj.checklist.date)
    species = SubFactory(SpeciesFactory)
    identified = LazyAttribute(lambda obj: obj.species.is_identified())
    checklist = SubFactory(ChecklistFactory)
    location = SubFactory(LocationFactory)
    country = LazyAttribute(lambda obj: obj.location.country)
    region = LazyAttribute(lambda obj: obj.location.region)
    district = LazyAttribute(lambda obj: obj.location.district)
    area = LazyAttribute(lambda obj: obj.location.area)
    observer = SubFactory(ObserverFactory)
    count = Faker("pyint")
    breeding_code = ""
    breeding_category = ""
    behavior_code = ""
    age_sex = ""
    reason = ""
    comments = ""
