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


@method_decorator(login_required, name="dispatch")
class NotificationsList(ListView):
    """
    Index page for authenticated user
    """

    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = notification_settings.PAGINATE_BY

    def get_queryset(self):
        filter_by = self.kwargs["filter_by"]
        if filter_by == "read":
            qset = self.request.user.notifications_notification_related.read()
        elif filter_by == "unread":
            qset = self.request.user.notifications_notification_related.unread()
        elif filter_by == "active":
            qset = self.request.user.notifications_notification_related.active()
        elif filter_by == "deleted":
            qset = self.request.user.notifications_notification_related.deleted()
        elif filter_by == "sent":
            qset = self.request.user.notifications_notification_related.sent()
        elif filter_by == "unsent":
            qset = self.request.user.notifications_notification_related.unsent()
        else:
            qset = self.request.user.notifications_notification_related.all()

        return qset


@login_required
def mark_all_as_read(request):
    request.user.notifications_notification_related.mark_all_as_read()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))
    return redirect("notifications:list", filter_by="unread")


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug

    notification = get_object_or_404(Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:list", filter_by="unread")


@login_required
def mark_as_unread(request, slug=None):
    notification_id = slug

    notification = get_object_or_404(Notification, recipient=request.user, id=notification_id)
    notification.mark_as_unread()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:list", filter_by="unread")


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

    return redirect("notifications:list", filter_by="unread")


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
