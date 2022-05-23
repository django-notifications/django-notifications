# -*- coding: utf-8 -*-
""" Django Notifications example views """
from distutils.version import \
    StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import ListView
from swapper import load_model

from notifications import settings
from notifications.settings import get_config
from notifications.utils import id2slug, slug2id

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
    paginate_by = settings.get_config()["PAGINATE_BY"]
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
        if settings.get_config()["SOFT_DELETE"]:
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

    if _next:
        return redirect(_next)
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

    if _next:
        return redirect(_next)

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

    if _next:
        return redirect(_next)

    return redirect("notifications:unread")


@login_required
def delete(request, slug=None):
    notification_id = slug2id(slug)

    current_site = get_current_site(request)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id, site=current_site
    )

    if settings.get_config()["SOFT_DELETE"]:
        notification.deleted = True
        notification.save()
    else:
        notification.delete()

    _next = request.GET.get("next")

    if _next:
        return redirect(_next)

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

    default_num_to_fetch = get_config()["NUM_TO_FETCH"]
    try:
        # If they don't specify, make it 5.
        num_to_fetch = request.GET.get("max", default_num_to_fetch)
        num_to_fetch = int(num_to_fetch)
        if not (1 <= num_to_fetch <= 100):
            num_to_fetch = default_num_to_fetch
    except ValueError:  # If casting to an int fails.
        num_to_fetch = default_num_to_fetch

    unread_list = []

    for notification in request.user.notifications.filter(site=current_site).unread()[
        0:num_to_fetch
    ]:
        struct = model_to_dict(notification)
        struct["slug"] = id2slug(notification.id)
        if notification.actor:
            struct["actor"] = str(notification.actor)
        if notification.target:
            struct["target"] = str(notification.target)
        if notification.action_object:
            struct["action_object"] = str(notification.action_object)
        if notification.data:
            struct["data"] = notification.data
        unread_list.append(struct)
        if request.GET.get("mark_as_read"):
            notification.mark_as_read()
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

    default_num_to_fetch = get_config()["NUM_TO_FETCH"]
    try:
        # If they don't specify, make it 5.
        num_to_fetch = request.GET.get("max", default_num_to_fetch)
        num_to_fetch = int(num_to_fetch)
        if not (1 <= num_to_fetch <= 100):
            num_to_fetch = default_num_to_fetch
    except ValueError:  # If casting to an int fails.
        num_to_fetch = default_num_to_fetch

    all_list = []

    for notification in request.user.notifications.filter(site=current_site).all()[
        0:num_to_fetch
    ]:
        struct = model_to_dict(notification)
        struct["slug"] = id2slug(notification.id)
        if notification.actor:
            struct["actor"] = str(notification.actor)
        if notification.target:
            struct["target"] = str(notification.target)
        if notification.action_object:
            struct["action_object"] = str(notification.action_object)
        if notification.data:
            struct["data"] = notification.data
        all_list.append(struct)
        if request.GET.get("mark_as_read"):
            notification.mark_as_read()
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
