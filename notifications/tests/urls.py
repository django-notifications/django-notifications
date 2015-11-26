# -*- coding: utf-8 -*-

from django.conf.urls import include, patterns, url
from django.contrib import admin

from notifications import urls

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'), # needed for Django 1.6 tests
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(urls, 'notifications')),
)
