# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-18 07:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commercialoperator', '0109_auto_20210513_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitycategory',
            name='activity_type',
            field=models.CharField(choices=[('land', 'Land'), ('marine', 'Marine'), ('Film', 'Film'), ('Event', 'Event')], default='land', max_length=40, verbose_name='Activity Type'),
        ),
    ]
