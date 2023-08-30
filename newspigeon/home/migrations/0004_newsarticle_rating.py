# Generated by Django 4.2.4 on 2023-08-25 18:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0003_pickleduser"),
    ]

    operations = [
        migrations.AddField(
            model_name="newsarticle",
            name="rating",
            field=models.IntegerField(
                default=None, validators=[django.core.validators.MaxValueValidator(10)]
            ),
        ),
    ]