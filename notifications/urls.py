''' Django notification urls file '''
# -*- coding: utf-8 -*-
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version

from . import views

if StrictVersion(get_version()) >= StrictVersion('2.0'):
    from django.urls import path as pattern
else:
    from django.conf.urls import url as pattern


urlpatterns = [
    pattern('', views.AllNotificationsList.as_view(), name='all'),
    pattern('unread/', views.UnreadNotificationsList.as_view(), name='unread'),
    pattern('mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
    pattern('mark-as-read/<slug:slug>/', views.mark_as_read, name='mark_as_read'),
    pattern('mark-as-unread/<slug:slug>/', views.mark_as_unread, name='mark_as_unread'),
    pattern('delete/<slug:slug>/', views.delete, name='delete'),
    pattern('api/unread_count/', views.live_unread_notification_count, name='live_unread_notification_count'),
    pattern('api/all_count/', views.live_all_notification_count, name='live_all_notification_count'),
    pattern('api/unread_list/', views.live_unread_notification_list, name='live_unread_notification_list'),
    pattern('api/all_list/', views.live_all_notification_list, name='live_all_notification_list'),
]

app_name = 'notifications'
