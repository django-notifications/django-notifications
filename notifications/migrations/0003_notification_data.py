# -*- coding: utf-8 -*-
from django.db import models, migrations


try:
    from jsonfield.fields import JSONField
except ModuleNotFoundError:
    JSONField = models.JSONField


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
