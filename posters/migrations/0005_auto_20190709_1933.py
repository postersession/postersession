# Generated by Django 2.0.10 on 2019-07-09 19:33

import constrainedfilefield.fields.file
from django.db import migrations, models
import unique_upload.unique_upload


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0004_auto_20190603_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='link_url',
            field=models.URLField(blank=True, max_length=256),
        ),
    ]
