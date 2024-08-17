"""Django notification urls for tests"""

# -*- coding: utf-8 -*-
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version
from django.contrib import admin

from notifications.tests.views import live_tester  # pylint: disable=no-name-in-module,import-error
from notifications.tests.views import make_notification

if StrictVersion(get_version()) >= StrictVersion("2.1"):
    from django.contrib.auth.views import LoginView
    from django.urls import include, path  # noqa

    urlpatterns = [
        path("test_make/", make_notification),
        path("test/", live_tester),
        path(
            "login/", LoginView.as_view(), name="login"
        ),  # reverse for django login is not working
        path("admin/", admin.site.urls),
        path("", include("notifications.urls", namespace="notifications")),
    ]
elif StrictVersion(get_version()) >= StrictVersion("2.0") and StrictVersion(
    get_version()
) < StrictVersion("2.1"):
    from django.contrib.auth.views import login
    from django.urls import include, path  # noqa

    urlpatterns = [
        path("test_make/", make_notification),
        path("test/", live_tester),
        path("login/", login, name="login"),  # reverse for django login is not working
        path("admin/", admin.site.urls),
        path("", include("notifications.urls", namespace="notifications")),
    ]
else:
    from django.contrib.auth.views import login
    from django.urls import include, path, re_path

    urlpatterns = [
        path("login/", login, name="login"),  # reverse for django login is not working
        re_path(r"^test_make/", make_notification),
        re_path(r"^test/", live_tester),
        path("", include("notifications.urls", namespace="notifications")),
        re_path(r"^admin/", admin.site.urls),
    ]
