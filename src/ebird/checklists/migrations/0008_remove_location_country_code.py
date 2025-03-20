# Generated by Django 5.1.7 on 2025-03-20 17:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checklists", "0007_set_country"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="location",
            name="country_code",
        ),
        migrations.RemoveField(
            model_name="location",
            name="country_name",
        ),
        migrations.AlterField(
            model_name="location",
            name="country",
            field=models.ForeignKey(
                help_text="The country for the location.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="locations",
                to="checklists.country",
                verbose_name="country",
            ),
        ),
    ]
