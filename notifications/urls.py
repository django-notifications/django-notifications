''' Django notification urls file '''
# -*- coding: utf-8 -*-
from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r'^$', views.AllNotificationsList.as_view(), name='all'),
    re_path(r'^unread/$', views.UnreadNotificationsList.as_view(), name='unread'),
    re_path(r'^mark-all-as-read/$', views.mark_all_as_read, name='mark_all_as_read'),
    re_path(r'^mark-as-read/(?P<slug>\d+)/$', views.mark_as_read, name='mark_as_read'),
    re_path(r'^mark-as-unread/(?P<slug>\d+)/$', views.mark_as_unread, name='mark_as_unread'),
    re_path(r'^delete/(?P<slug>\d+)/$', views.delete, name='delete'),
    re_path(r'^api/unread_count/$', views.live_unread_notification_count, name='live_unread_notification_count'),
    re_path(r'^api/all_count/$', views.live_all_notification_count, name='live_all_notification_count'),
    re_path(r'^api/unread_list/$', views.live_unread_notification_list, name='live_unread_notification_list'),
    re_path(r'^api/all_list/', views.live_all_notification_list, name='live_all_notification_list'),
]

app_name = 'notifications'
