# Generated by Django 2.2.10 on 2020-04-05 17:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("emails", "0008_deletedaddress"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deletedaddress",
            name="address_hash",
            field=models.CharField(db_index=True, max_length=64),
        ),
    ]
