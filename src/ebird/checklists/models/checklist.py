import datetime
from dateutil import relativedelta
import re

from django.db import models
from django.utils.translation import gettext_lazy as _

# All the protocols from Appendices 2 and 3 of the eBird Basic Dataset
# Metadata V1.14 description.

PROTOCOL_TYPE = {
    "P22": _("Travelling"),
    "P21": _("Stationary"),
    "P62": _("Historical"),
    "P20": _("Incidental"),
    "P23": _("Area"),
    "P33": _("Banding"),
    "P60": _("Pelagic"),
    "P54": _("Nocturnal Flight Call Count"),
    "P52": _("Oiled Birds"),
    "P48": _("Random"),
    "P59": _("TNC California Waterbird Count"),
    "P46": _("CWC Point Count"),
    "P47": _("CWC Area Search"),
    "P80": _("CWC Travelling Count"),
    "P41": _("Rusty Blackbird Spring Migration Blitz"),
    "P69": _("California Brown Pelican Survey"),
    "P73": _("PROALAS Point Count (2 Bands)"),
    "P81": _("PROALAS Mini-transect"),
    "P82": _("PROALAS Point Count (3 Bands)"),
    "P83": _("Orange-breasted Falcon Site Survey"),
    "P58": _("Audubon Coastal Bird Survey"),
    "P74": _("International Shorebird Survey"),
    "P84": _("Migratory Shorebird Protocol"),
    "P70": _("BirdLife Australia 20min-2ha survey"),
    "P72": _("BirdLife Australia 5 km radius search"),
    "P71": _("BirdLife Australia 500m radius search"),
    "P66": _("Birds 'n' Bogs Survey"),
    "P65": _("Breeding Bird Atlas"),
    "P67": _("Common Bird Survey"),
    "P50": _("Caribbean Martin Survey"),
    "P49": _("Coastal Shorebird Survey"),
    "P57": _("Great Texas Birding Classic"),
    "P51": _("Greater Gulf Refuge Waterbird Count"),
    "P56": _("Heron Area Count"),
    "P55": _("Heron Stationary Count"),
    "P61": _("IBA Canada"),
    "P39": _("LoonWatch"),
    "P35": _("My Yard Counts"),
    "P68": _("RAM--Iberian Seawatch Network"),
    "P40": _("Standardized Yard Count"),
    "P30": _("Trail Tracker"),
    "P75": _("Tricolored Blackbird Winter Survey"),
    "P64": _("Traveling - Property Specific"),
    "P34": _("Waterbird Count"),
    "P44": _("Yellow-billed Magpie Survey - General Observations"),
    "P45": _("Yellow-billed Magpie Survey - Traveling Count"),
}

class ChecklistQuerySet(models.QuerySet):

    def for_country(self, value: str):
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
        return self.filter(date__gte=start).filter(date__lt=until)

    def for_month(self, year: int, month: int):
        start = datetime.date(year, month, 1)
        until = start + relativedelta.relativedelta(months=1)
        return self.filter(date__gte=start).filter(date__lt=until)

    def for_day(self, year: int, month: int, day: int):
        date = datetime.date(year, month, day)
        return self.filter(date=date)

    def for_date(self, date: datetime.date):
        return self.filter(date=date)


class Checklist(models.Model):

    class Meta:
        verbose_name = _("checklist")
        verbose_name_plural = _("checklists")

    created = models.DateTimeField(
        auto_now_add=True,
        help_text=_("The date and time the checklist was created"),
        verbose_name=_("created"),
    )

    modified = models.DateTimeField(
        auto_now=True,
        help_text=_("The date and time the checklist was modified"),
        verbose_name=_("modified"),
    )

    edited = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("The date and time the eBird checklist was last edited"),
        verbose_name=_("edited"),
    )

    identifier = models.TextField(
        verbose_name=_("identifier"),
        help_text=_("The unique identifier for the checklist.")
    )

    location = models.ForeignKey(
        "checklists.Location",
        related_name="checklists",
        on_delete=models.PROTECT,
        verbose_name=_("location"),
        help_text=_("The location where checklist was made.")
    )

    observer = models.ForeignKey(
        "checklists.Observer",
        related_name="checklists",
        on_delete=models.PROTECT,
        verbose_name=_("observer"),
        help_text=_("The person who submitted the checklist."),
    )

    group = models.TextField(
        blank=True,
        verbose_name=_("group"),
        help_text=_("The identifier for a group of observers."),
    )

    observer_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("observer count"),
        help_text=_("The total number of observers.")
    )

    species_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("species count"),
        help_text=_("The number of species reported.")
    )

    date = models.DateField(
        verbose_name=_("date"),
        help_text=_("The date the checklist was made.")
    )

    time = models.TimeField(
        blank=True,
        null=True,
        verbose_name=_("time"),
        help_text=_("The time the checklist was started.")
    )

    protocol = models.TextField(
        blank=True,
        verbose_name=_("protocol"),
        help_text=_("The protocol followed, e.g. travelling, stationary, etc."),
    )

    protocol_code = models.TextField(
        blank=True,
        verbose_name=_("protocol code"),
        help_text=_("The code used to identify the protocol."),
    )

    project_code = models.TextField(
        blank=True,
        verbose_name=_("project code"),
        help_text=_("The code used to identify the project (portal)."),
    )

    duration = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("duration"),
        help_text=_("The number of minutes spent counting.")
    )

    distance = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        verbose_name=_("distance"),
        help_text=_("The distance, in metres, covered while travelling.")
    )

    area = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        verbose_name=_("area"),
        help_text=_("The area covered, in hectares.")
    )

    complete = models.BooleanField(
        default=False,
        verbose_name=_("complete"),
        help_text=_("All species seen are reported.")
    )

    comments = models.TextField(
        blank=True,
        verbose_name=_("comments"),
        help_text=_("Any comments about the checklist."),
    )

    url = models.URLField(
        blank=True,
        verbose_name=_("url"),
        help_text=_("URL where the original checklist can be viewed."),
    )

    objects = ChecklistQuerySet.as_manager()

    def __str__(self):
        return "%s %s, %s" % (
            self.date, self.time, self.location.name
        )
