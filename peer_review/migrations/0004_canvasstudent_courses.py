# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-07 15:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peer_review', '0003_auto_20180418_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='canvasstudent',
            name='courses',
            field=models.ManyToManyField(related_name='students', to='peer_review.CanvasCourse'),
        ),
    ]
