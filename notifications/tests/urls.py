''' Django notification urls for tests '''
# -*- coding: utf-8 -*-
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version
from django.contrib import admin
from notifications.tests.views import (live_tester,  # pylint: disable=no-name-in-module,import-error
                                       make_notification)

if StrictVersion(get_version()) >= StrictVersion('2.1'):
    from django.urls import include, path  # noqa
    from django.contrib.auth.views import LoginView
    urlpatterns = [
        path('test_make/', make_notification),
        path('test/', live_tester),
        path('login/', LoginView.as_view(), name='login'),  # reverse for django login is not working
        path('admin/', admin.site.urls),
        path('', include('notifications.urls', namespace='notifications')),
    ]
elif StrictVersion(get_version()) >= StrictVersion('2.0') and StrictVersion(get_version()) < StrictVersion('2.1'):
    from django.urls import include, path  # noqa
    from django.contrib.auth.views import login
    urlpatterns = [
        path('test_make/', make_notification),
        path('test/', live_tester),
        path('login/', login, name='login'),  # reverse for django login is not working
        path('admin/', admin.site.urls),
        path('', include('notifications.urls', namespace='notifications')),
    ]
else:
    from django.conf.urls import include, url
    from django.contrib.auth.views import login
    urlpatterns = [
        url(r'^login/$', login, name='login'),  # reverse for django login is not working
        url(r'^test_make/', make_notification),
        url(r'^test/', live_tester),
        url(r'^', include('notifications.urls', namespace='notifications')),
        url(r'^admin/', admin.site.urls),
    ]
