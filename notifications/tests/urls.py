# -*- coding: utf-8 -*-

from django.conf.urls import include, patterns, url
from django.contrib import admin

import notifications

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(notifications.urls)),
)