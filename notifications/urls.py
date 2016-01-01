# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views


app_name = 'notifications'
urlpatterns = [
    url(r'^$', views.AllNotificationsList.as_view(), name='all'),
    url(r'^unread/$', views.UnreadNotificationsList.as_view(), name='unread'),
    url(r'^mark-all-as-read/$', views.mark_all_as_read, name='mark_all_as_read'),
    url(r'^mark-as-read/(?P<slug>\d+)/$', views.mark_as_read, name='mark_as_read'),
    url(r'^mark-as-unread/(?P<slug>\d+)/$', views.mark_as_unread, name='mark_as_unread'),
    url(r'^delete/(?P<slug>\d+)/$', views.delete, name='delete'),
    url(r'^api/unread_count/$', views.live_unread_notification_count, name='live_unread_notification_count'),
    url(r'^api/unread_list/$', views.live_unread_notification_list, name='live_unread_notification_list'),
]
