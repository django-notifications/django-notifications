''' Django notifications admin file '''
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import gettext_lazy
from notifications.base.admin import AbstractNotificationAdmin
from swapper import load_model

Notification = load_model('notifications', 'Notification')


def mark_unread(modeladmin, request, queryset):
    queryset.update(unread=True)
mark_unread.short_description = gettext_lazy('Mark selected notifications as unread')


class NotificationAdmin(AbstractNotificationAdmin):
    raw_id_fields = ('recipient',)
    readonly_fields = ('action_object_url', 'actor_object_url', 'target_object_url')
    list_display = ('recipient', 'actor',
                    'level', 'target', 'unread', 'public')
    list_filter = ('level', 'unread', 'public', 'timestamp',)
    actions = [mark_unread]

    def get_queryset(self, request):
        qs = super(NotificationAdmin, self).get_queryset(request)
        return qs.prefetch_related('actor')


admin.site.register(Notification, NotificationAdmin)
