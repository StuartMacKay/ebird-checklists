from django.db import models
from django.utils.translation import gettext_lazy as _

class ObserverQuerySet(models.QuerySet):
    pass


class Observer(models.Model):

    class Meta:
        verbose_name = _("observer")
        verbose_name_plural = _("observers")

    created = models.DateTimeField(
        auto_now_add=True,
        help_text=_("The date and time the observer was created"),
        verbose_name=_("created"),
    )

    modified = models.DateTimeField(
        auto_now=True,
        help_text=_("The date and time the observer was modified"),
        verbose_name=_("modified"),
    )

    identifier = models.TextField(
        verbose_name=_("identifier"),
        help_text=_("The code for the person submitted the checklist."),
    )

    name = models.TextField(
        blank=True,
        verbose_name=_("name"),
        help_text=_("The observer's name."),
    )

    objects = ObserverQuerySet.as_manager()

    def __str__(self):
        return self.name
