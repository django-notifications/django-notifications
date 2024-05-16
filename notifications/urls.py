""" Django notification urls file """
# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = "notifications"
urlpatterns = [
    path("list/<str:filter_by>/", views.NotificationsList.as_view(), name="list"),
    path("mark-all-as/<str:status>/", views.NotificationsMarkAll.as_view(), name="mark_all_as"),
    path("mark/<uuid:uuid>/as/<str:status>/", views.NotificationsMarkAs.as_view(), name="mark_as"),
    path("api/<str:filter_by>/", views.NotificationsAPI.as_view(), name="api"),
]
