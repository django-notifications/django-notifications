''' Django notifications admin file '''
# -*- coding: utf-8 -*-
from django.contrib import admin
from swapper import load_model

Notification = load_model('notifications', 'Notification')

def mark_unread(modeladmin, request, queryset):
    queryset.update(unread=True)
mark_unread.short_description = "Mark selected notifications as unread"

class NotificationAdmin(admin.ModelAdmin):
    raw_id_fields = ('recipient',)
    list_display = ('recipient', 'actor',
                    'level', 'target', 'unread', 'public')
    list_filter = ('level', 'unread', 'public', 'timestamp',)
    actions = [mark_unread]

    def get_queryset(self, request):
        qs = super(NotificationAdmin, self).get_queryset(request)
        return qs.prefetch_related('actor')


admin.site.register(Notification, NotificationAdmin)
