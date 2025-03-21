# Generated by Django 5.1.7 on 2025-03-20 16:50

from django.db import migrations


def set_region(apps, schema_editor):
    Location = apps.get_model("checklists", "Location")
    Region = apps.get_model("checklists", "Region")
    for location in Location.objects.all():
        region, created = Region.objects.get_or_create(
            code=location.state_code,
            defaults={
                "name": location.state,
                "place": "%s, %s" % (location.state, location.country.name),
            }
        )
        location.region = region
        location.save()


class Migration(migrations.Migration):

    dependencies = [
        ("checklists", "0009_add_region"),
    ]

    operations = [
        migrations.RunPython(set_region),
    ]
