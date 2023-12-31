# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-16 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peer_review', '0006_remove_canvasstudent_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='rubric',
            name='peer_review_evaluation_due_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rubric',
            name='peer_review_evaluation_is_mandatory',
            field=models.BooleanField(default=True),
        ),
    ]
