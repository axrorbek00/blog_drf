# Generated by Django 4.2.6 on 2023-12-21 06:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0003_postviews_following"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="like_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
