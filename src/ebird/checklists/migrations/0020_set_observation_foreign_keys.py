# Generated by Django 5.1.7 on 2025-03-20 16:50

import django.db.models.deletion
from django.db import migrations, models


def set_checklist_foreign_keys(apps, schema_editor):
    Observation = apps.get_model("checklists", "Observation")
    for observation in Observation.objects.all():
        location = observation.location
        observation.country = location.country
        observation.region = location.region
        observation.district = location.district
        observation.area = location.area
        observation.save()


class Migration(migrations.Migration):

    dependencies = [
        ("checklists", "0019_set_checklist_foreign_keys"),
    ]

    operations = [
        migrations.RunPython(set_checklist_foreign_keys),
        migrations.AlterField(
            model_name="observation",
            name="country",
            field=models.ForeignKey(
                help_text="The country where the observation was made.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="observations",
                to="checklists.country",
                verbose_name="country",
            ),
        ),
        migrations.AlterField(
            model_name="observation",
            name="region",
            field=models.ForeignKey(
                help_text="The region where the observation was made.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="observations",
                to="checklists.region",
                verbose_name="region",
            ),
        ),
    ]
