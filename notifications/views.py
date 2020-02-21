# -*- coding: utf-8 -*-
''' Django Notifications example views '''
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from notifications import settings
from notifications.models import Notification
from notifications.utils import id2slug, slug2id
from notifications.settings import get_config
from django.views.decorators.cache import never_cache

if StrictVersion(get_version()) >= StrictVersion('1.7.0'):
    from django.http import JsonResponse  # noqa
else:
    # Django 1.6 doesn't have a proper JsonResponse
    import json
    from django.http import HttpResponse  # noqa

    def date_handler(obj):
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj

    def JsonResponse(data):  # noqa
        return HttpResponse(
            json.dumps(data, default=date_handler),
            content_type="application/json")


class NotificationViewList(ListView):
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = settings.get_config()['PAGINATE_BY']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationViewList, self).dispatch(
            request, *args, **kwargs)


class AllNotificationsList(NotificationViewList):
    """
    Index page for authenticated user
    """

    def get_queryset(self):
        if settings.get_config()['SOFT_DELETE']:
            qset = self.request.user.notifications.active()
        else:
            qset = self.request.user.notifications.all()
        return qset


class UnreadNotificationsList(NotificationViewList):

    def get_queryset(self):
        return self.request.user.notifications.unread()


@login_required
def mark_all_as_read(request):
    request.user.notifications.mark_all_as_read()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)
    return redirect('notifications:unread')


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)

    return redirect('notifications:unread')


@login_required
def mark_as_unread(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_unread()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)

    return redirect('notifications:unread')


@login_required
def delete(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)

    if settings.get_config()['SOFT_DELETE']:
        notification.deleted = True
        notification.save()
    else:
        notification.delete()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)

    return redirect('notifications:all')


def get_notification_count(request, count_types=("all", "unread")):
    counts = {}
    try:
        notifications = request.user.notifications
    except AttributeError:  # user is not logged in
        notifications = None

    def get_count(count_type):
        if notifications:
            return notifications.__getattribute__(count_type)().count()
        else:
            return 0
    for ct in count_types:
        counts["{}_count".format(ct)] = get_count(ct)
    return counts


@never_cache
def live_unread_notification_count(request):
    return JsonResponse(get_notification_count(request, ("unread",)))


@never_cache
def live_all_notification_count(request):
    return JsonResponse(get_notification_count(request, ("all",)))


@never_cache
def live_notification_count(request):
    return JsonResponse(get_notification_count(request, ("all", "unread")))


def get_notification_list(request, selections=("all", "unread"), count_types=("all", "unread")):
    try:
        notifications = request.user.notifications
    except AttributeError:  # User is not logged in
        notifications = None

    data = {}
    if notifications is None:
        for st in selections:
            data['{}_list'.format(st)] = []
            data.update(get_notification_count(request, count_types))
        return data

    default_num_to_fetch = get_config()['NUM_TO_FETCH']
    try:
        # If they don't specify, make it 5.
        num_to_fetch = request.GET.get('max', default_num_to_fetch)
        num_to_fetch = int(num_to_fetch)
        if not (1 <= num_to_fetch <= 100):
            num_to_fetch = default_num_to_fetch
    except ValueError:  # If casting to an int fails.
        num_to_fetch = default_num_to_fetch

    for st in selections:
        notification_list = []

        for notification in notifications.__getattribute__(st)()[0:num_to_fetch]:
            struct = model_to_dict(notification)
            struct['slug'] = id2slug(notification.id)
            if notification.actor:
                struct['actor'] = str(notification.actor)
            if notification.target:
                struct['target'] = str(notification.target)
            if notification.action_object:
                struct['action_object'] = str(notification.action_object)
            if notification.data:
                struct['data'] = notification.data
            notification_list.append(struct)
            if request.GET.get('mark_as_read'):
                notification.mark_as_read()
        data['{}_list'.format(st)] = notification_list
    data.update(get_notification_count(request, count_types))
    return data


@never_cache
def live_unread_notification_list(request):
    ''' Return a json with a unread notification list '''
    return JsonResponse(get_notification_list(request, ("unread",), ("unread",)))


@never_cache
def live_all_notification_list(request):
    ''' Return a json with a unread notification list '''
    return JsonResponse(get_notification_list(request, ("all",)))
