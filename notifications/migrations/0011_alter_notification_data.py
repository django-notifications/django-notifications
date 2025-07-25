# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0008_index_together_recipient_unread'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='data',
            field=models.JSONField(null=True, blank=True),
        ),
    ]
