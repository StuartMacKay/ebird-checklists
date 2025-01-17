import re

from django.db import connection, models
from django.utils.translation import gettext_lazy as _

LOCATION_TYPE = {
    "C": _("County"),
    "H": _("Hotspot"),
    "P": _("Personal"),
    "PC": _("Postal/Zip Code"),
    "S": _("State"),
    "T": _("Town"),
}


class LocationQuerySet(models.QuerySet):
    def for_country(self, code: str):
        if not re.match(r"[A-Z]{2}", code):
            raise ValueError("Unsupported country code: %s" % code)
        return self.filter(country_code=code)

    def for_state(self, code: str):
        if not re.match(r"[A-Z]{2}-[A-Z0-9]{2,3}", code):
            raise ValueError("Unsupported state code: %s" % code)
        return self.filter(state_code=code)

    def for_county(self, code: str):
        if not re.match(r"[A-Z]{2}-[A-Z0-9]{2,3}-[A-Z0-9]{2,3}", code):
            raise ValueError("Unsupported county code: %s" % code)
        return self.filter(county_code=code)

    def for_identifier(self, identifier: str):
        return self.get(identifier=identifier)


class LocationManager(models.Manager):
    def country_choices(self):
        vendor = connection.vendor
        queryset = self.all().values_list("country_code", "country")
        if vendor == "sqlite":
            return list({(country_code, country) for country_code, country in queryset})
        else:
            return queryset.distinct("country_code")

    def country_choice(self, code):
        return (
            self.filter(country_code=code)
            .values_list("country_code", "country")
            .first()
        )

    def state_choices(self, code):
        vendor = connection.vendor
        queryset = self.filter(country_code=code).values_list(
            "state_code", "state"
        )
        if vendor == "sqlite":
            return list({(state_code, state) for state_code, state in queryset})
        else:
            return queryset.distinct("state_code")

    def state_choice(self, code):
        return self.filter(state_code=code).values_list("state_code", "state").first()

    def county_choices(self, code):
        vendor = connection.vendor
        queryset = self.filter(state_code=code).values_list("county_code", "county")
        if vendor == "sqlite":
            return list({(county_code, county) for county_code, county in queryset})
        else:
            return queryset.distinct("county_code")

    def county_choice(self, code):
        return self.filter(county_code=code).values_list("county_code", "county").first()


class Location(models.Model):
    class Meta:
        verbose_name = _("location")
        verbose_name_plural = _("locations")

    created = models.DateTimeField(
        auto_now_add=True,
        help_text=_("The date and time the location was created"),
        verbose_name=_("created"),
    )

    modified = models.DateTimeField(
        auto_now=True,
        help_text=_("The date and time the location was modified"),
        verbose_name=_("modified"),
    )

    identifier = models.TextField(
        verbose_name=_("identifier"),
        help_text=_("The unique identifier for the location"),
    )

    type = models.TextField(
        blank=True,
        verbose_name=_("type"),
        help_text=_("The location type, e.g. personal, hotspot, town, etc."),
    )

    name = models.TextField(
        verbose_name=_("name"), help_text=_("The name of the location")
    )

    county = models.TextField(
        blank=True,
        verbose_name=_("county"),
        help_text=_("The name of the county (subnational2)."),
    )

    county_code = models.TextField(
        blank=True,
        verbose_name=_("county code"),
        help_text=_("The code used to identify the county."),
    )

    state = models.TextField(
        verbose_name=_("state"), help_text=_("The name of the state (subnational1).")
    )

    state_code = models.TextField(
        verbose_name=_("state code"),
        help_text=_("The code used to identify the state."),
    )

    country = models.TextField(
        verbose_name=_("country"), help_text=_("The name of the country.")
    )

    country_code = models.TextField(
        verbose_name=_("country code"),
        help_text=_("The code used to identify the country."),
    )

    iba_code = models.TextField(
        blank=True,
        verbose_name=_("IBA code"),
        help_text=_("The code used to identify an Important Bird Area."),
    )

    bcr_code = models.TextField(
        blank=True,
        verbose_name=_("BCR code"),
        help_text=_("The code used to identify a Bird Conservation Region."),
    )

    usfws_code = models.TextField(
        blank=True,
        verbose_name=_("USFWS code"),
        help_text=_("The code used to identify a US Fish & Wildlife Service region."),
    )

    atlas_block = models.TextField(
        blank=True,
        verbose_name=_("atlas block"),
        help_text=_("The code used to identify an area for an atlas."),
    )

    latitude = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=7,
        max_digits=9,
        verbose_name=_("latitude"),
        help_text=_("The decimal latitude of the location, relative to the equator"),
    )

    longitude = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=7,
        max_digits=10,
        verbose_name=_("longitude"),
        help_text=_(
            "The decimal longitude of the location, relative to the prime meridian"
        ),
    )

    url = models.URLField(
        blank=True,
        verbose_name=_("url"),
        help_text=_("URL of the location page on eBird."),
    )

    hotspot = models.BooleanField(
        blank=True,
        null=True,
        verbose_name=_("is hotspot"),
        help_text=_("Is the location a hotspot"),
    )

    objects = LocationManager.from_queryset(LocationQuerySet)()

    def __str__(self):
        return self.name
