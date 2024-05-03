""" Django notifications apps file """
# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.core.signals import setting_changed
from django.utils.translation import gettext_lazy as _


class Config(AppConfig):
    name = "notifications"
    verbose_name = _("Notifications")
    default_auto_field = "django.db.models.AutoField"

    def ready(self) -> None:
        from notifications.settings import (  # pylint: disable=import-outside-toplevel
            reload_notification_settings,
        )
        from notifications.signals import (  # pylint: disable=import-outside-toplevel
            notify,
            notify_handler,
        )

        notify.connect(notify_handler, dispatch_uid="notifications.models.notification")
        setting_changed.connect(reload_notification_settings, dispatch_uid="notifications.models.notification")

        return super().ready()
