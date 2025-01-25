import random
import string

import factory
from django.utils.timezone import get_default_timezone

from ebird.checklists.models import (Checklist, Location, Observation, Observer,
                                     Species)

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


def random_state_code(country_code: str) -> str:
    return random_uppercase(2, f"{country_code}-")


def url(category: str, code: str) -> str:
    return f"https://ebird.org/{category}/{code}"


def hotspot_url(code: str) -> str:
    return url("hotspot", code)


def checklist_url(code: str) -> str:
    return url("checklist", code)


def random_county_code(country_code: str) -> str:
    state_code = random_state_code(country_code)
    county_code = random_uppercase(random.randint(2, 3))
    return f"{country_code}-{state_code}-{county_code}"


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location
        django_get_or_create = ("identifier", )

    identifier = factory.LazyAttribute(lambda _: random_code(6, "L"))
    type = ""
    name = factory.Faker("street_name")
    county = factory.Faker("city")  # OK for now
    county_code = factory.LazyAttribute(lambda o: random_county_code(o.country_code))
    state = factory.Faker("city")  # OK for now
    state_code = factory.LazyAttribute(lambda o: random_state_code(o.country_code))
    country = factory.Faker("country")
    country_code = factory.Faker("country_code")
    iba_code = ""
    bcr_code = ""
    usfws_code = ""
    atlas_block = ""
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")
    url = factory.LazyAttribute(lambda o: hotspot_url(o.identifier))
    hotspot = True


class ObserverFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Observer
        django_get_or_create = ("name",)

    identifier = factory.LazyAttribute(lambda _: random_code(7, "obsr"))
    name = factory.Faker("name")


class SpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Species
        django_get_or_create = ("taxon_order", )

    taxon_order = factory.LazyAttribute(lambda _: random.randint(100000, 1000000))
    species_code = factory.LazyAttribute(lambda _: random_lowercase(6))
    family_code = factory.LazyAttribute(lambda _: random_lowercase(6))
    category = ""
    common_name = factory.LazyAttribute(lambda _: random_key(SPECIES))
    scientific_name = factory.LazyAttribute(lambda obj: SPECIES[obj.common_name])
    subspecies_common_name = ""
    subspecies_scientific_name = ""
    family_common_name = ""
    family_scientific_name = ""
    exotic_code = ""


class ChecklistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Checklist

    created = factory.Faker("date_time", tzinfo=get_default_timezone())
    edited = factory.Faker("date_time", tzinfo=get_default_timezone())
    identifier = factory.LazyAttribute(lambda _: random_code(9, "S"))
    location = factory.SubFactory(LocationFactory)
    observer = factory.SubFactory(ObserverFactory)
    observer_count = random.randint(1, 5)
    date = factory.Faker("date_object")
    time = factory.Faker("time_object")
    group = ""
    protocol = factory.LazyAttribute(lambda obj: PROTOCOLS[obj.protocol_code])
    protocol_code = factory.LazyAttribute(lambda _: random_key(PROTOCOLS))
    project_code = factory.LazyAttribute(lambda _: random.choice(PROJECTS))
    complete = True
    comments = ""
    url = factory.LazyAttribute(lambda o: checklist_url(o.identifier))


class ObservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Observation

    identifier = factory.LazyAttribute(lambda _: random_code(10, "OBS"))
    species = factory.SubFactory(SpeciesFactory)
    checklist = factory.SubFactory(ChecklistFactory)
    location = factory.SubFactory(LocationFactory)
    observer = factory.SubFactory(ObserverFactory)
    count = factory.Faker("pyint")
    breeding_code = ""
    breeding_category = ""
    behavior_code = ""
    age_sex = ""
    reason = ""
    comments = ""
