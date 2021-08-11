''' Django notifications admin file '''
# -*- coding: utf-8 -*-
from django.contrib import admin
from notifications.base.admin import AbstractNotificationAdmin
from swapper import load_model

Notification = load_model('notifications', 'Notification')


class NotificationAdmin(AbstractNotificationAdmin):
    pass


admin.site.register(Notification, NotificationAdmin)
