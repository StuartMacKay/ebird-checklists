# pyright: reportOptionalMemberAccess=false

from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea, TextInput
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from . import models


class ObservationInline(admin.TabularInline):
    model = models.Observation
    fields = ("common_name", "scientific_name", "count", "comments")
    ordering = ("species__order",)
    readonly_fields = ("common_name", "scientific_name", "count", "comments")
    extra = 0

    class Media:
        css = {"all": ("css/hide_admin_original.css",)}

    @admin.display(description=_("Common name"))
    def common_name(self, obj):
        url = reverse(
            "admin:checklists_observation_change", kwargs={"object_id": obj.id}
        )
        return format_html('<a href="{}">{}</a>', url, obj.species.common_name)

    @admin.display(description=_("Scientific name"))
    def scientific_name(self, obj):
        return format_html("<i>{}</i>", obj.species.scientific_name)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("species")
            .order_by("species__taxon_order")
        )


@admin.register(models.Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = (
        "identifier",
        "date",
        "time",
        "species_count",
        "location",
        "observer",
    )
    list_select_related = (
        "location",
        "observer",
    )
    ordering = ("-started",)
    search_fields = ("location__name", "observer__name")
    autocomplete_fields = ("location", "observer")
    inlines = [ObservationInline]
    formfield_overrides = {
        TextField: {
            "widget": TextInput(attrs={"style": "width: 30%"}),
        }
    }
    readonly_fields = ("identifier", "edited")
    fields = (
        "date",
        "time",
        "location",
        "observer",
        "species_count",
        "complete",
        "observer_count",
        "group",
        "protocol",
        "protocol_code",
        "duration",
        "distance",
        "area",
        "comments",
        "data",
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        text_fields = (
            "observer_count",
            "species_count",
            "duration",
            "distance",
            "area'",
        )

        if db_field.name in text_fields:
            field.widget = TextInput()
        elif db_field.name == "comments":
            field.widget = Textarea(attrs={"rows": 5, "style": "width: 60%"})

        return field

    def save_model(self, request, obj, form, change):
        if 'location' in form.changed_data:
            location = obj.location
            obj.country = location.country
            obj.region = location.region
            obj.district = location.district
            obj.area = location.area
        super().save_model(request,obj, form, change)


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("code",)


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("code",)


@admin.register(models.District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("code",)


@admin.register(models.Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("code",)


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("identifier", "name", "district", "region", "country")
    ordering = ("-identifier",)
    search_fields = ("name", "district__name", "region__name", "country__name")
    formfield_overrides = {
        TextField: {
            "widget": TextInput(attrs={"style": "width: 30%"}),
        }
    }
    readonly_fields = ("identifier",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "latitude":
            field.widget = TextInput()
        elif db_field.name == "longitude":
            field.widget = TextInput()
        return field

    def save_model(self, request, obj, form, change):
        super().save_model(request,obj, form, change)
        if 'country' in form.changed_data:
            models.Checklist.objects.filter(location=obj).update(country=obj.country)
            models.Observation.objects.filter(location=obj).update(country=obj.country)
        if 'region' in form.changed_data:
            models.Checklist.objects.filter(location=obj).update(region=obj.region)
            models.Observation.objects.filter(location=obj).update(region=obj.region)
        if 'district' in form.changed_data:
            models.Checklist.objects.filter(location=obj).update(district=obj.district)
            models.Observation.objects.filter(location=obj).update(district=obj.district)
        if 'area' in form.changed_data:
            models.Checklist.objects.filter(location=obj).update(area=obj.area)
            models.Observation.objects.filter(location=obj).update(area=obj.area)


@admin.register(models.Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = (
        "species__common_name",
        "count",
        "checklist__date",
        "checklist__time",
        "location",
        "observer",
    )
    search_fields = (
        "species__common_name",
        "species__scientific_name",
        "observer__name",
    )
    ordering = ("-checklist__started",)
    formfield_overrides = {
        TextField: {
            "widget": TextInput(attrs={"style": "width: 30%"}),
        }
    }
    autocomplete_fields = ("checklist", "location", "observer", "species")
    readonly_fields = ("identifier", "edited")
    fields = (
        "species",
        "count",
        "age_sex",
        "breeding_code",
        "breeding_category",
        "behavior_code",
        "media",
        "comments",
        "checklist",
        "location",
        "observer",
        "edited",
        "approved",
        "reviewed",
        "reason",
        "data",
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "comments":
            field.widget = Textarea(attrs={"rows": 5, "style": "width: 60%"})
        elif db_field.name == "count":
            field.widget = TextInput()
        return field

    def save_model(self, request, obj, form, change):
        if 'location' in form.changed_data:
            location = obj.location
            obj.country = location.country
            obj.region = location.region
            obj.district = location.district
            obj.area = location.area
        super().save_model(request,obj, form, change)


@admin.register(models.Observer)
class ObserverAdmin(admin.ModelAdmin):
    list_display = ("name", "identifier")
    ordering = ("name",)
    search_fields = ("name", "identifier")
    formfield_overrides = {TextField: {"widget": TextInput}}


@admin.register(models.Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = (
        "common_name",
        "scientific_name",
        "family_common_name",
        "family_scientific_name",
        "order",
    )
    ordering = ("order",)
    search_fields = ("common_name", "scientific_name")
    formfield_overrides = {
        TextField: {
            "widget": TextInput(attrs={"style": "width: 30%"}),
        }
    }
    readonly_fields = ("taxon_order",)
    fields = (
        "common_name",
        "scientific_name",
        "species_code",
        "order",
        "category",
        "exotic_code",
        "subspecies_common_name",
        "subspecies_scientific_name",
        "family_common_name",
        "family_scientific_name",
        "family_code",
        "data",
    )
