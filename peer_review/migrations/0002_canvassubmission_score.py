# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-23 15:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peer_review', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='canvassubmission',
            name='score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]