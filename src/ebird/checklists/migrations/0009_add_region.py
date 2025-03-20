# Generated by Django 5.1.7 on 2025-03-20 17:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checklists", "0008_remove_location_country_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="Region",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        db_index=True,
                        help_text="The code used to identify the region.",
                        max_length=6,
                        verbose_name="code",
                    ),
                ),
                (
                    "name",
                    models.TextField(
                        help_text="The name of the region.", verbose_name="name"
                    ),
                ),
                (
                    "place",
                    models.TextField(
                        help_text="The hierarchical name of the region.",
                        verbose_name="place",
                    ),
                ),
            ],
            options={
                "verbose_name": "region",
                "verbose_name_plural": "regions",
            },
        ),
        migrations.AddField(
            model_name="location",
            name="region",
            field=models.ForeignKey(
                blank=True,
                help_text="The region for the location.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="locations",
                to="checklists.region",
                verbose_name="region",
            ),
        ),
    ]
