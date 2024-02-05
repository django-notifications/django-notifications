# -*- coding: utf-8 -*-
""" Django Notifications example views """
from distutils.version import (
    StrictVersion,
)  # pylint: disable=no-name-in-module,import-error

from django import get_version
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.generic import ListView
from swapper import load_model

from notifications import settings as notification_settings
from notifications.helpers import get_notification_list
from notifications.utils import slug2id

Notification = load_model("notifications", "Notification")

if StrictVersion(get_version()) >= StrictVersion("1.7.0"):
    from django.http import JsonResponse  # noqa
else:
    # Django 1.6 doesn't have a proper JsonResponse
    import json

    from django.http import HttpResponse  # noqa

    def date_handler(obj):
        return obj.isoformat() if hasattr(obj, "isoformat") else obj

    def JsonResponse(data):  # noqa
        return HttpResponse(
            json.dumps(data, default=date_handler), content_type="application/json"
        )


class NotificationViewList(ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = notification_settings.get_config()["PAGINATE_BY"]
    queryset = Notification.on_site

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationViewList, self).dispatch(request, *args, **kwargs)


class AllNotificationsList(NotificationViewList):
    """
    Index page for authenticated user
    """

    def get_queryset(self):
        current_site = get_current_site(self.request)
        if notification_settings.get_config()["SOFT_DELETE"]:
            qset = self.request.user.notifications.filter(site=current_site).active()
        else:
            qset = self.request.user.notifications.filter(site=current_site).all()
        return qset


class UnreadNotificationsList(NotificationViewList):
    def get_queryset(self):
        current_site = get_current_site(self.request)
        return self.request.user.notifications.filter(site=current_site).unread()


@login_required
def mark_all_as_read(request):
    current_site = get_current_site(request)
    request.user.notifications.filter(site=current_site).mark_all_as_read()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))
    return redirect("notifications:unread")


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)

    current_site = get_current_site(request)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id, site=current_site
    )
    notification.mark_as_read()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:unread")


@login_required
def mark_as_unread(request, slug=None):
    notification_id = slug2id(slug)

    current_site = get_current_site(request)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id, site=current_site
    )
    notification.mark_as_unread()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:unread")


@login_required
def delete(request, slug=None):
    notification_id = slug2id(slug)

    current_site = get_current_site(request)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id, site=current_site
    )

    if notification_settings.get_config()["SOFT_DELETE"]:
        notification.deleted = True
        notification.save()
    else:
        notification.delete()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:all")


@never_cache
def live_unread_notification_count(request):
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    current_site = get_current_site(request)

    if not user_is_authenticated:
        data = {"unread_count": 0}
    else:
        data = {
            "unread_count": request.user.notifications.filter(site=current_site)
            .unread()
            .count(),
        }
    return JsonResponse(data)


@never_cache
def live_unread_notification_list(request):
    """Return a json with a unread notification list"""
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    current_site = get_current_site(request)

    if not user_is_authenticated:
        data = {"unread_count": 0, "unread_list": []}
        return JsonResponse(data)

    unread_list = get_notification_list(request, "unread")

    data = {
        "unread_count": request.user.notifications.filter(site=current_site)
        .unread()
        .count(),
        "unread_list": unread_list,
    }
    return JsonResponse(data)


@never_cache
def live_all_notification_list(request):
    """Return a json with a unread notification list"""
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    current_site = get_current_site(request)

    if not user_is_authenticated:
        data = {"all_count": 0, "all_list": []}
        return JsonResponse(data)

    all_list = get_notification_list(request)

    data = {
        "all_count": request.user.notifications.filter(site=current_site).count(),
        "all_list": all_list,
    }
    return JsonResponse(data)


def live_all_notification_count(request):
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    current_site = get_current_site(request)

    if not user_is_authenticated:
        data = {"all_count": 0}
    else:
        data = {
            "all_count": request.user.notifications.filter(site=current_site).count(),
        }
    return JsonResponse(data)
