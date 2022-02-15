''' Django notification urls for tests '''
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from notifications.tests.views import (live_tester,  # pylint: disable=no-name-in-module,import-error
                                       make_notification)


urlpatterns = [
    path('test_make/', make_notification),
    path('test/', live_tester),
    path('login/', LoginView.as_view(), name='login'),  # reverse for django login is not working
    path('admin/', admin.site.urls),
    path('', include('notifications.urls', namespace='notifications')),
]
