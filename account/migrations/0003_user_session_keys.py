# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2019-12-22 16:02
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_remove_user_session_keys'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='session_keys',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list),
        ),
    ]
