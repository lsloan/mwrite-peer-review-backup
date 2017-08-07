# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-04 17:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peer_review', '0011_rubric_sections'),
    ]

    operations = [
        migrations.AlterField(
            model_name='canvasstudent',
            name='sections',
            field=models.ManyToManyField(blank=True, related_name='students', to='peer_review.CanvasSection'),
        ),
    ]
