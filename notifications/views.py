# -*- coding: utf-8 -*-
""" Django Notifications example views """
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import ListView, RedirectView
from swapper import load_model

from notifications.helpers import get_limit, queryset_to_dict, str_to_bool
from notifications.mixins import NotificationRedirectMixin
from notifications.settings import notification_settings

Notification = load_model("notifications", "Notification")


@method_decorator(login_required, name="dispatch")
class NotificationsList(ListView):
    """
    List notifications for the authenticated user
    """

    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = notification_settings.PAGINATE_BY

    def get_queryset(self):
        filter_by = self.kwargs["filter_by"]
        method = getattr(self.request.user.notifications_notification_related, filter_by, None)
        if method:
            qset = method()
        else:
            qset = self.request.user.notifications_notification_related.all()

        return qset


@method_decorator(login_required, name="dispatch")
class NotificationsMarkAll(NotificationRedirectMixin, RedirectView):
    """
    Change the status for all notifications for authenticated user
    """

    def get(self, request, *args, **kwargs):
        status = self.kwargs["status"]
        method_name = f"mark_all_as_{status}"
        method = getattr(request.user.notifications_notification_related, method_name, None)
        if not method:
            return HttpResponseNotFound(f'Status "{status}" not exists.')

        method()

        return HttpResponseRedirect(self.get_redirect_url())


@method_decorator(login_required, name="dispatch")
class NotificationsMarkAs(NotificationRedirectMixin, RedirectView):
    """
    Change the status for one notification for authenticated user
    """

    def get(self, request, *args, **kwargs):
        status = self.kwargs["status"]
        notification_uuid = self.kwargs["uuid"]

        notification = get_object_or_404(Notification, recipient=request.user, uuid=notification_uuid)

        method = getattr(notification, f"mark_as_{status}", None)
        if not method:
            return HttpResponseNotFound(f'Status "{status}" not exists.')

        method()
        return HttpResponseRedirect(self.get_redirect_url())


@method_decorator(never_cache, name="dispatch")
class NotificationsAPI(View):
    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        if not request.user.is_authenticated:
            return HttpResponseForbidden("User not authenticated.")

        filter_by = self.kwargs["filter_by"]
        should_count = str_to_bool(request.GET.get("count", False))
        mark_as_read = str_to_bool(request.GET.get("mark_as_read", False))
        limit = get_limit(request)
        method = getattr(request.user.notifications_notification_related, filter_by, None)

        if not method:
            return HttpResponseNotFound(f'Status "{method}" not exists.')

        data = {"list": queryset_to_dict(method(), limit)}

        if mark_as_read:
            ids = method()[:limit].values_list("id", flat=True)
            request.user.notifications_notification_related.filter(id__in=ids).mark_as_read()

        if should_count:
            data["count"] = method().count()

        return JsonResponse(data)
