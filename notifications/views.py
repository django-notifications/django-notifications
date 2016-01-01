from django import get_version
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from .utils import slug2id
from .models import Notification

from distutils.version import StrictVersion
if StrictVersion(get_version()) >= StrictVersion('1.7.0'):
    from django.http import JsonResponse
else:
    # Django 1.6 doesn't have a proper JsonResponse
    import json
    from django.http import HttpResponse

    def date_handler(obj):
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj

    def JsonResponse(data):
        return HttpResponse(
            json.dumps(data, default=date_handler),
            content_type="application/json")


class NotificationViewList(ListView):
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationViewList, self).dispatch(
            request, *args, **kwargs)


class AllNotificationsList(NotificationViewList):
    """
    Index page for authenticated user
    """

    def get_queryset(self):
        if getattr(settings, 'NOTIFICATIONS_SOFT_DELETE', False):
            qs = self.request.user.notifications.active()
        else:
            qs = self.request.user.notifications.all()
        return qs


class UnreadNotificationsList(NotificationViewList):

    def get_queryset(self):
        return self.request.user.notifications.unread()


@login_required
def mark_all_as_read(request):
    request.user.notifications.mark_all_as_read()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)
    return redirect('notifications:all')


@login_required
def mark_as_read(request, slug=None):
    id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=id)
    notification.mark_as_read()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)

    return redirect('notifications:all')


@login_required
def mark_as_unread(request, slug=None):
    id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=id)
    notification.mark_as_unread()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)

    return redirect('notifications:all')


@login_required
def delete(request, slug=None):
    _id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=_id)

    if getattr(settings, 'NOTIFICATIONS_SOFT_DELETE', False):
        notification.deleted = True
        notification.save()
    else:
        notification.delete()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)

    return redirect('notifications:all')


def live_unread_notification_count(request):
    data = {
        'unread_count': request.user.notifications.unread().count(),
    }
    return JsonResponse(data)


def live_unread_notification_list(request):

    try:
        num_to_fetch = request.GET.get('max', 5)  # If they don't specify, make it 5.
        num_to_fetch = int(num_to_fetch)
        num_to_fetch = max(1, num_to_fetch)  # if num_to_fetch is negative, force at least one fetched notifications
        num_to_fetch = min(num_to_fetch, 100)  # put a sane ceiling on the number retrievable
    except ValueError:
        num_to_fetch = 5  # If casting to an int fails, just make it 5.

    unread_list = []

    for n in request.user.notifications.unread()[0:num_to_fetch]:
        struct = model_to_dict(n)
        if n.actor:
            struct['actor'] = str(n.actor)
        if n.target:
            struct['target'] = str(n.target)
        if n.action_object:
            struct['action_object'] = str(n.action_object)
        unread_list.append(struct)
    data = {
        'unread_count': request.user.notifications.unread().count(),
        'unread_list': unread_list
    }
    return JsonResponse(data)
