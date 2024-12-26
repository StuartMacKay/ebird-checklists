import datetime
from dateutil import relativedelta
import re

from django.db import models
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

    def for_country(self, value:str):
        if re.match(r"[A-Z]{2,3}", value):
            return self.filter(location__country_code=value)
        else:
            return self.filter(location__country=value)

    def for_state(self, value: str):
        if re.match(r"[A-Z]{2}-[A-Z0-9]{2,3}", value):
            return self.filter(location__state_code=value)
        else:
            return self.filter(location__state=value)

    def for_county(self, value: str):
        if re.match(r"[A-Z]{2,3}-[A-Z0-9]{2,3}-[A-Z0-9]{2,3}", value):
            return self.filter(location__county_code=value)
        else:
            return self.filter(location__county=value)

    def for_year(self, year: int):
        start = datetime.date(year, 1, 1)
        until = datetime.date(year + 1, 1, 1)
        return self.filter(date__gte=start).filter(date_lt=until)

    def for_month(self, year: int, month: int):
        start = datetime.date(year, month, 1)
        until = start + relativedelta.relativedelta(months=1)
        return self.filter(date__gte=start).filter(date_lt=until)

    def for_day(self, year: int, month: int, day: int):
        date = datetime.date(year, month, day)
        return self.filter(date=date)

    def for_date(self, date: datetime.date):
        return self.filter(date=date)


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
        help_text=_("The unique identifier for the location")
    )

    type = models.TextField(
        blank=True,
        verbose_name=_("type"),
        help_text=_("The location type, e.g. personal, hotspot, town, etc.")
    )

    name = models.TextField(
        verbose_name=_("name"),
        help_text=_("The name of the location")
    )

    county = models.TextField(
        blank=True,
        verbose_name=_("county"),
        help_text=_("The name of the county (subnational2).")
    )

    county_code = models.TextField(
        blank=True,
        verbose_name=_("county code"),
        help_text=_("The code used to identify the county.")
    )

    state = models.TextField(
        verbose_name = _("state"),
        help_text = _("The name of the state (subnational1).")
    )

    state_code = models.TextField(
        verbose_name = _("state code"),
        help_text = _("The code used to identify the state.")
    )

    country = models.TextField(
        verbose_name=_("country"),
        help_text=_("The name of the country.")
    )

    country_code = models.TextField(
        verbose_name=_("country code"),
        help_text=_("The code used to identify the country.")
    )

    iba_code = models.TextField(
        blank=True,
        verbose_name=_("IBA code"),
        help_text=_("The code used to identify an Important Bird Area.")
    )

    bcr_code = models.TextField(
        blank=True,
        verbose_name=_("BCR code"),
        help_text=_("The code used to identify a Bird Conservation Region.")
    )

    usfws_code = models.TextField(
        blank=True,
        verbose_name=_("USFWS code"),
        help_text=_("The code used to identify a US Fish & Wildlife Service region.")
    )

    atlas_block = models.TextField(
        blank=True,
        verbose_name=_("atlas block"),
        help_text=_("The code used to identify an area for an atlas.")
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
            "The decimal longitude of the location, relative to the prime meridian"),
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

    objects = LocationQuerySet.as_manager()

    def __str__(self):
        return self.name
