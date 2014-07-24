# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'actor',
                    'level', 'target', 'unread', 'public')
    list_filter = ('level', 'unread', 'public', 'timestamp', )

admin.site.register(Notification, NotificationAdmin)
