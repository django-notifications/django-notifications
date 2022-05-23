""" Django notifications admin file """
# -*- coding: utf-8 -*-
from django.contrib import admin
from swapper import load_model

from notifications.base.admin import AbstractNotificationAdmin

Notification = load_model("notifications", "Notification")


class NotificationAdmin(AbstractNotificationAdmin):
    raw_id_fields = ("recipient",)
    list_display = ("recipient", "actor", "level", "target", "unread", "public", "site")
    list_filter = ("level", "unread", "public", "timestamp", "site")

    def get_queryset(self, request):
        qs = super(NotificationAdmin, self).get_queryset(request)
        return qs.prefetch_related("actor")


admin.site.register(Notification, NotificationAdmin)
