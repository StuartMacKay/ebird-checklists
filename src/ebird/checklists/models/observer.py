from django.db import models
from django.utils.translation import gettext_lazy as _

class ObserverQuerySet(models.QuerySet):
    pass


class Observer(models.Model):

    class Meta:
        verbose_name = _("observer")
        verbose_name_plural = _("observers")

    identifier = models.TextField(
        verbose_name=_("identifier"),
        help_text=_("The code for the person submitted the checklist."),
    )

    name = models.TextField(
        blank=True,
        verbose_name=_("name"),
        help_text=_("The observer's name."),
    )

    data = models.JSONField(
        verbose_name=_("Data"),
        help_text=_("Data describing an Observer."),
        default=dict,
        blank=True,
    )

    objects = ObserverQuerySet.as_manager()

    def __str__(self):
        return self.name
