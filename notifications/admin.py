""" Django notifications admin file """
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy
from swapper import load_model

from notifications.querysets import NotificationQuerySet

Notification = load_model("notifications", "Notification")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    raw_id_fields = ("recipient",)
    readonly_fields = ("action_object_url", "actor_object_url", "target_object_url")
    list_display = ("recipient", "actor", "level", "target", "unread", "public")
    list_filter = (
        "level",
        "unread",
        "public",
        "timestamp",
    )
    actions = ("mark_unread", "mark_read")

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        return qs.prefetch_related("actor")

    @admin.action(description=gettext_lazy("Mark selected notifications as unread"))
    def mark_unread(self, request: HttpRequest, queryset: NotificationQuerySet):  # pylint: disable=unused-argument
        queryset.mark_as_unread()

    @admin.action(description=gettext_lazy("Mark selected notifications as read"))
    def mark_read(self, request: HttpRequest, queryset: NotificationQuerySet):  # pylint: disable=unused-argument
        queryset.mark_as_read()
