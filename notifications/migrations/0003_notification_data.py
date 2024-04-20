# -*- coding: utf-8 -*-
from django.db import migrations, models

try:
    from jsonfield.fields import JSONField
except ImportError:
    from django.db.models import JSONField


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0002_auto_20150224_1134"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="data",
            field=JSONField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
