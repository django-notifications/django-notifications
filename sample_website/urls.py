""" Django notification urls for tests """
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import include, path

from sample_website.views import live_tester, make_notification

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path("test_make/", make_notification),
    path("admin/", admin.site.urls),
    path("", include("notifications.urls", namespace="notifications")),
    path("", live_tester),
]
