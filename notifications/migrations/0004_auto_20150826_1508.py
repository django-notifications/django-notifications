# -*- coding: utf-8 -*-
from django.db import models, migrations
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_notification_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.DateTimeField(default=timezone.now),
        ),
    ]
