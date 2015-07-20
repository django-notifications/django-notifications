# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('notifications.views',
    url(r'^$', 'all', name='all'),
    url(r'^unread/$', 'unread', name='unread'),
    url(r'^mark-all-as-read/$', 'mark_all_as_read', name='mark_all_as_read'),
    url(r'^mark-as-read/(?P<slug>\d+)/$', 'mark_as_read', name='mark_as_read'),
    url(r'^mark-as-unread/(?P<slug>\d+)/$', 'mark_as_unread', name='mark_as_unread'),
    url(r'^delete/(?P<slug>\d+)/$', 'delete', name='delete'),
    url(r'^api/unread_count/$', 'live_unread_notification_count', name='live_unread_notification_count'),
    url(r'^api/unread_list/$', 'live_unread_notification_list', name='live_unread_notification_list'),
)
