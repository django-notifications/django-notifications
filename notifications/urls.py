# -*- coding: utf-8 -*-
from distutils.version import StrictVersion

from django import get_version

from . import views

if StrictVersion(get_version()) >= StrictVersion('2.0'):
    from django.urls import include, path
    urlpatterns = [
        path('', views.AllNotificationsList.as_view(), name='all'),
        path('unread/', views.UnreadNotificationsList.as_view(), name='unread'),
        path('mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
        path('mark-as-read/<slug:slug>/', views.mark_as_read, name='mark_as_read'),
        path('mark-as-unread/<slug:slug>/', views.mark_as_unread, name='mark_as_unread'),
        path('delete/<slug:slug>/', views.delete, name='delete'),
        path('api/unread_count/', views.live_unread_notification_count, name='live_unread_notification_count'),
        path('api/unread_list/', views.live_unread_notification_list, name='live_unread_notification_list'),
    ]
else:
    from django.contrib import admin
    from django.conf.urls import include, url
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

app_name = 'notifications'
