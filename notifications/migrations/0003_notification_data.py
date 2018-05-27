# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django import get_version
from distutils.version import StrictVersion
if StrictVersion(get_version()) >= StrictVersion('1.9.0'):
    from django.contrib.postgres.fields import JSONField
else:
    from jsonfield.fields import JSONField


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20150224_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='data',
            field=JSONField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
