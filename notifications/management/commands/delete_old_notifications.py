from __future__ import unicode_literals

import click
import logging
from datetime import datetime, timedelta
from django.core.management.base import LabelCommand

from ... import models

logger = logging.getLogger(__name__)


class Command(LabelCommand):
    def handle(self, *labels, **options):
        if len(labels) != 1:
            click.echo(click.style(
                "Please pass maximum age in seconds so notifications older than it will be deleted", fg='red'))
            return
        logger.info('Start deletion of old notifications process')
        age_in_seconds = int(labels[0])
        time_now = datetime.now()
        time_before = time_now - timedelta(seconds=age_in_seconds)
        models.Notification.objects.filter(timestamp__lte=time_before).delete()
        logger.info('Deletion completed')
