# -*- coding: utf-8 -*-

from django.conf.urls import include, patterns, url
from django.contrib import admin

from notifications import urls

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'), # needed for Django 1.6 tests
    url(r'^admin/', include(admin.site.urls)),
    url(r'^test_make/', 'notifications.tests.views.make_notification'),
    url(r'^test/', 'notifications.tests.views.live_tester'),
    url(r'^', include(urls, 'notifications')),
)
