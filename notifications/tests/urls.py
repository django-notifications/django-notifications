# -*- coding: utf-8 -*-
from distutils.version import StrictVersion
from django import get_version
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login

import notifications.urls
import notifications.tests.views

urlpatterns = [
    url(r'^login/$', login, name='login'),  # needed for Django 1.6 tests
    url(r'^test_make/', notifications.tests.views.make_notification),
    url(r'^test/', notifications.tests.views.live_tester),
    url(r'^', include(notifications.urls, namespace='notifications')),
]

if StrictVersion(get_version()) >= StrictVersion('2.0'):
    urlpatterns.append(url(r'^admin/', admin.site.urls))
else:
    urlpatterns.append(url(r'^admin/', include(admin.site.urls)))
