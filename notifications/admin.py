# -*- coding: utf-8 -*-

from django.contrib import admin
from notifications.models import Notification

class NotificationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Notification, NotificationAdmin)
