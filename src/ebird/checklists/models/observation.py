import datetime
from dateutil import relativedelta
import re

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class ObservationQuerySet(models.QuerySet):
    def for_country(self, code: str):
        if not re.match(r"[A-Z]{2}", code):
            raise ValueError("Unsupported country code: %s" % code)
        return self.filter(location__country_code=code)

    def for_state(self, code: str):
        if not re.match(r"[A-Z]{2}-[A-Z0-9]{2,3}", code):
            raise ValueError("Unsupported state code: %s" % code)
        return self.filter(location__state_code=code)

    def for_county(self, code: str):
        if not re.match(r"[A-Z]{2}-[A-Z0-9]{2,3}-[A-Z0-9]{2,3}", code):
            raise ValueError("Unsupported county code: %s" % code)
        return self.filter(location__county_code=code)

    def for_location(self, identifier: str):
        if not re.match(r"L\d+", identifier):
            raise ValueError("Unsupported location identifier: %s" % identifier)
        return self.filter(location__identifier=identifier)

    def for_identifier(self, identifier: str):
        return self.get(identifier=identifier)

    def for_date(self, date: datetime.date):
        return self.filter(checklist__date=date)

    def for_dates(self, start: datetime.date, end: datetime.date):
        return self.filter(checklist__date__gte=start).filter(checklist__date__lt=end)

    def for_observer(self, value: str):
        if re.match(r"obsr\d+", value):
            return self.filter(observer__identifier=value)
        else:
            return self.filter(observer__name__exact=value)


class Observation(models.Model):
    class Meta:
        verbose_name = _("observation")
        verbose_name_plural = _("observations")

    edited = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("The date and time the eBird checklist was last edited"),
        verbose_name=_("edited"),
    )

    identifier = models.TextField(
        unique=True,
        verbose_name=_("identifier"),
        help_text=_("A global unique identifier for the observation."),
    )

    checklist = models.ForeignKey(
        "checklists.Checklist",
        related_name="observations",
        on_delete=models.CASCADE,
        verbose_name=_("checklist"),
        help_text=_("The checklist this observation belongs to."),
    )

    species = models.ForeignKey(
        "checklists.Species",
        related_name="observations",
        on_delete=models.PROTECT,
        verbose_name=_("species"),
        help_text=_("The identified species."),
    )

    observer = models.ForeignKey(
        "checklists.Observer",
        related_name="observations",
        on_delete=models.PROTECT,
        verbose_name=_("observer"),
        help_text=_("The person who made the observation."),
    )

    location = models.ForeignKey(
        "checklists.Location",
        related_name="observations",
        on_delete=models.PROTECT,
        verbose_name=_("location"),
        help_text=_("The location where the observation was made."),
    )

    count = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("count"),
        help_text=_("The number of birds seen."),
    )

    breeding_code = models.TextField(
        blank=True,
        verbose_name=_("breeding code"),
        help_text=_("eBird code identifying the breeding status"),
    )

    breeding_category = models.TextField(
        blank=True,
        verbose_name=_("breeding category"),
        help_text=_("eBird code identifying the breeding category"),
    )

    behavior_code = models.TextField(
        blank=True,
        verbose_name=_("behaviour code"),
        help_text=_("eBird code identifying the behaviour"),
    )

    age_sex = models.TextField(
        blank=True,
        verbose_name=_("Age & Sex"),
        help_text=_("The number of birds seen in each combination of age and sex."),
    )

    media = models.BooleanField(
        blank=True,
        null=True,
        verbose_name=_("has media"),
        help_text=_("Has audio, photo or video uploaded to the Macaulay library."),
    )

    approved = models.BooleanField(
        blank=True,
        null=True,
        verbose_name=_("Approved"),
        help_text=_("Has the observation been accepted by eBird's review process."),
    )

    reviewed = models.BooleanField(
        blank=True,
        null=True,
        verbose_name=_("Reviewed"),
        help_text=_("Was the observation reviewed because it failed automatic checks."),
    )

    reason = models.TextField(
        blank=True,
        verbose_name=_("Reason"),
        help_text=_(
            "The reason given for the observation to be marked as not confirmed."
        ),
    )

    comments = models.TextField(
        blank=True,
        verbose_name=_("comments"),
        help_text=_("Any comments about the observation."),
    )

    urn = models.TextField(
        blank=True,
        verbose_name=_("URN"),
        help_text=_("The globally unique identifier for the observation"),
    )

    data = models.JSONField(
        verbose_name=_("Data"),
        help_text=_("Data describing an Observation."),
        default=dict,
        blank=True,
    )

    objects = ObservationQuerySet.as_manager()

    def __str__(self):
        return "%s (%s)" % (self.species.common_name, self.count)
