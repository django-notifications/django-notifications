# -*- coding: utf-8 -*-
""" Django Notifications example views """
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.generic import ListView
from swapper import load_model

from notifications.helpers import get_notification_list
from notifications.settings import notification_settings

Notification = load_model("notifications", "Notification")


class NotificationViewList(ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = notification_settings.PAGINATE_BY

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AllNotificationsList(NotificationViewList):
    """
    Index page for authenticated user
    """

    def get_queryset(self):
        if notification_settings.SOFT_DELETE:
            qset = self.request.user.notifications_notification_related.active()
        else:
            qset = self.request.user.notifications_notification_related.all()
        return qset


class UnreadNotificationsList(NotificationViewList):
    def get_queryset(self):
        return self.request.user.notifications_notification_related.unread()


@login_required
def mark_all_as_read(request):
    request.user.notifications_notification_related.mark_all_as_read()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))
    return redirect("notifications:unread")


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug

    notification = get_object_or_404(Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:unread")


@login_required
def mark_as_unread(request, slug=None):
    notification_id = slug

    notification = get_object_or_404(Notification, recipient=request.user, id=notification_id)
    notification.mark_as_unread()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:unread")


@login_required
def delete(request, slug=None):
    notification_id = slug

    notification = get_object_or_404(Notification, recipient=request.user, id=notification_id)

    if notification_settings.SOFT_DELETE:
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
    if not request.user.is_authenticated:
        data = {"unread_count": 0}
    else:
        data = {
            "unread_count": request.user.notifications_notification_related.unread().count(),
        }
    return JsonResponse(data)


@never_cache
def live_unread_notification_list(request):
    """Return a json with a unread notification list"""
    if not request.user.is_authenticated:
        data = {"unread_count": 0, "unread_list": []}
        return JsonResponse(data)

    unread_list = get_notification_list(request, "unread")

    data = {
        "unread_count": request.user.notifications_notification_related.unread().count(),
        "unread_list": unread_list,
    }
    return JsonResponse(data)


@never_cache
def live_all_notification_list(request):
    """Return a json with a unread notification list"""
    if not request.user.is_authenticated:
        data = {"all_count": 0, "all_list": []}
        return JsonResponse(data)

    all_list = get_notification_list(request)

    data = {"all_count": request.user.notifications_notification_related.count(), "all_list": all_list}
    return JsonResponse(data)


def live_all_notification_count(request):
    if not request.user.is_authenticated:
        data = {"all_count": 0}
    else:
        data = {
            "all_count": request.user.notifications_notification_related.count(),
        }
    return JsonResponse(data)
