# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login

import notifications.urls
import notifications.tests.views

urlpatterns = [
    url(r'^login/$', login, name='login'),  # needed for Django 1.6 tests
    url(r'^admin/', include(admin.site.urls)),
    url(r'^test_make/', notifications.tests.views.make_notification),
    url(r'^test/', notifications.tests.views.live_tester),
    url(r'^', include(notifications.urls, namespace='notifications')),
]
