from django.db import models
from notifications.base.models import AbstractNotification


class Notification(AbstractNotification):
    details = models.CharField(max_length=64, blank=True, null=True)

    class Meta(AbstractNotification.Meta):
        abstract = False
