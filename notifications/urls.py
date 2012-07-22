# -*- coding: utf-8 -*-

from django.conf.urls import *

urlpatterns = patterns('notifications.views',
    url(r'^$', 'list', name='notifications_list'),
    url(r'^read_all/$', 'read_all', name='notifications_read_all'),
    url(r'^read/(?P<slug>\d+)/$', 'read', name='notifications_read'),
)
