# Generated by Django 5.1.7 on 2025-03-21 14:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checklists", "0016_rename_checklist_area"),
    ]

    operations = [
        migrations.AddField(
            model_name="checklist",
            name="area",
            field=models.ForeignKey(
                blank=True,
                help_text="The area where the checklist was made.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="checklists",
                to="checklists.area",
                verbose_name="area",
            ),
        ),
        migrations.AddField(
            model_name="checklist",
            name="country",
            field=models.ForeignKey(
                blank=True,
                help_text="The country where the checklist was made.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="checklists",
                to="checklists.country",
                verbose_name="country",
            ),
        ),
        migrations.AddField(
            model_name="checklist",
            name="district",
            field=models.ForeignKey(
                blank=True,
                help_text="The district where the checklist was made.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="checklists",
                to="checklists.district",
                verbose_name="district",
            ),
        ),
        migrations.AddField(
            model_name="checklist",
            name="region",
            field=models.ForeignKey(
                blank=True,
                help_text="The region where the checklist was made.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="checklists",
                to="checklists.region",
                verbose_name="region",
            ),
        ),
    ]
