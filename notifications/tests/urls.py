# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login


urlpatterns = [
    url(r'^login/$', login, name='login'), # needed for Django 1.6 tests
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('notifications.urls', namespace='notifications')),
]
