''' Django notifications admin file '''
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Notification
from .filters import ArchivedFilter, ReadFilter, SeenFilter


class NotificationAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('General'), {
            'fields': (
                'level', 'recipient',
            )
        }),
        (_('Actor'), {
            'fields': (
                'actor_content_type', 'actor_object_id',
            )
        }),
        (_('Content'), {
            'fields': (
                'verb', 'description'
            )
        }),
        (_('Target'), {
            'fields': (
                'target_content_type', 'target_object_id',
            )
        }),
        (_('Action'), {
            'fields': (
                'action_object_content_type', 'action_object_object_id',
            )
        }),
        (_('Dates'), {
            'fields': (
                'created_at', 'archived_at', 'read_at', 'seen_at'
            )
        }),
        (_('Other'), {
            'fields': (
                'data',
            )
        }),
    )

    raw_id_fields = (
        'recipient',
    )
    list_display = (
        'recipient', 'actor', 'level', 'target', 'archived',
        'read', 'seen',
    )
    list_filter = (
        'level', 'created_at', 'archived_at',
        ArchivedFilter, ReadFilter, SeenFilter
    )

    def archived(self, obj):
        return obj.archived_at is not None
    archived.boolean = True

    def read(self, obj):
        return obj.read_at is not None
    read.boolean = True

    def seen(self, obj):
        return obj.seen_at is not None
    seen.boolean = True


admin.site.register(Notification, NotificationAdmin)
