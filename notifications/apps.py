''' Django notifications apps file '''
# -*- coding: utf-8 -*-
from django.apps import AppConfig


class Config(AppConfig):
    name = "notifications"

    def ready(self):
        super(Config, self).ready()
        # this is for backwards compability
        import notifications.signals
        notifications.notify = notifications.signals.notify
