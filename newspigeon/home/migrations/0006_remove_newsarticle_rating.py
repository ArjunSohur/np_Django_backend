# Generated by Django 4.2.4 on 2023-08-25 20:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0005_alter_newsarticle_rating"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="newsarticle",
            name="rating",
        ),
    ]
