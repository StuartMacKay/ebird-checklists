# Generated by Django 5.1.5 on 2025-02-01 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checklists", "0005_checklist_started"),
    ]

    operations = [
        migrations.AlterField(
            model_name="checklist",
            name="date",
            field=models.DateField(
                db_index=True,
                help_text="The date the checklist was started.",
                verbose_name="date",
            ),
        ),
        migrations.AlterField(
            model_name="checklist",
            name="identifier",
            field=models.TextField(
                help_text="The unique identifier for the checklist.",
                unique=True,
                verbose_name="identifier",
            ),
        ),
        migrations.AlterField(
            model_name="checklist",
            name="started",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                help_text="The date and time the checklist was started.",
                null=True,
                verbose_name="date & time",
            ),
        ),
        migrations.AlterField(
            model_name="location",
            name="country_code",
            field=models.TextField(
                db_index=True,
                help_text="The code used to identify the country.",
                verbose_name="country code",
            ),
        ),
        migrations.AlterField(
            model_name="location",
            name="county_code",
            field=models.TextField(
                blank=True,
                db_index=True,
                help_text="The code used to identify the county.",
                verbose_name="county code",
            ),
        ),
        migrations.AlterField(
            model_name="location",
            name="identifier",
            field=models.TextField(
                help_text="The unique identifier for the location",
                unique=True,
                verbose_name="identifier",
            ),
        ),
        migrations.AlterField(
            model_name="location",
            name="state_code",
            field=models.TextField(
                db_index=True,
                help_text="The code used to identify the state.",
                verbose_name="state code",
            ),
        ),
        migrations.AlterField(
            model_name="observation",
            name="identifier",
            field=models.TextField(
                help_text="A global unique identifier for the observation.",
                unique=True,
                verbose_name="identifier",
            ),
        ),
        migrations.AlterField(
            model_name="observer",
            name="name",
            field=models.TextField(
                blank=True,
                help_text="The observer's name.",
                unique=True,
                verbose_name="name",
            ),
        ),
    ]
