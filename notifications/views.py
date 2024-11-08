# -*- coding: utf-8 -*-
''' Django Notifications example views '''
from distutils.version import \
    StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.generic import ListView
from swapper import load_model


from rest_framework import permissions, status, pagination
from rest_framework.response import Response
from rest_framework.decorators import action
from notifications.serializers import NotificationSerializer
from notifications.viewsets import NotificationsBaseViewSet

from notifications import settings as notification_settings
from notifications.helpers import get_notification_list
from notifications.utils import slug2id

Notification = load_model('notifications', 'Notification')

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
    paginate_by = notification_settings.get_config()['PAGINATE_BY']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationViewList, self).dispatch(
            request, *args, **kwargs)


class AllNotificationsList(NotificationViewList):
    """
    Index page for authenticated user
    """

    def get_queryset(self):
        if notification_settings.get_config()['SOFT_DELETE']:
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

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))
    return redirect('notifications:unread')


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()

    _next = request.GET.get('next')

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect('notifications:unread')


@login_required
def mark_as_unread(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_unread()

    _next = request.GET.get('next')

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect('notifications:unread')


@login_required
def delete(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)

    if notification_settings.get_config()['SOFT_DELETE']:
        notification.deleted = True
        notification.save()
    else:
        notification.delete()

    _next = request.GET.get('next')

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect('notifications:all')


@never_cache
def live_unread_notification_count(request):
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {
            'unread_count': 0
        }
    else:
        data = {
            'unread_count': request.user.notifications.unread().count(),
        }
    return JsonResponse(data)


@never_cache
def live_unread_notification_list(request):
    ''' Return a json with a unread notification list '''
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {
            'unread_count': 0,
            'unread_list': []
        }
        return JsonResponse(data)

    unread_list = get_notification_list(request, 'unread')

    data = {
        'unread_count': request.user.notifications.unread().count(),
        'unread_list': unread_list
    }
    return JsonResponse(data)


@never_cache
def live_all_notification_list(request):
    ''' Return a json with a unread notification list '''
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {
            'all_count': 0,
            'all_list': []
        }
        return JsonResponse(data)

    all_list = get_notification_list(request)

    data = {
        'all_count': request.user.notifications.count(),
        'all_list': all_list
    }
    return JsonResponse(data)


def live_all_notification_count(request):
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {
            'all_count': 0
        }
    else:
        data = {
            'all_count': request.user.notifications.count(),
        }
    return JsonResponse(data)


class NotificationsViewSet(NotificationsBaseViewSet):

    """
    This viewset that provides the following actions `retrieve()`, `update()`, `destroy()` and `list()`.
    `retrieve()`: is used to retrieve the object related to the user and mark it as read
    `update()`: is used to update the object related to the user by mark it as unread
    `destroy()`: is used to deleting object related to the user depending on the settings if settings.get_config()['SOFT_DELETE']
    `list()`: is used to retrieve all the objects related to the user
    `access_all()`: is used to retrieve all the objects related to the user and mark them as read with a post request
    `access_all()`: is used to retrieve all the objects related to the user and mark them as unread with a put request
    `access_all()`: is used to retrieve all the objects related to the user and delete them,\n
    depending on the settings if settings.get_config()['SOFT_DELETE'] with a delete request
    `unread_notification_list()`: is used to retrieve all the objects related to the user that are not read
    `unread_count()`: is used to retrieve the number objects that are not read and related to the user
    `notifications_count()`: is used to retrieve the number objects that are  related to the user
    """

    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = (pagination.PageNumberPagination)
    lookup_field = 'id'

    
    def perform_destroy(self,instance):
        if settings.get_config()['SOFT_DELETE']:
            instance.deleted = True
            instance.save()
        else:
            instance.delete()

    @action(["get"], detail=False)
    def unread_count(self, request, *args, **kwargs):
        data = {
            'unread_count': request.user.notifications.unread().count(),
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(["get"], detail=False)
    def notifications_count(self, request, *args, **kwargs):
        data = {
            'count': request.user.notifications.active().count(),
        }
        return Response(data, status=status.HTTP_200_OK)
    
    @action(["get"], detail=False)
    def unread_notification_list(self, request, *args, **kwargs):
        queryset = request.user.notifications.unread().filter(deleted=False).order_by("-timestamp")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(["post", "put", "delete"], detail=False)
    def access_all(self, request, *args, **kwargs):
        if request.method == "POST":
            request.user.notifications.active().mark_all_as_read()
            return Response(status=status.HTTP_200_OK)
        elif request.method == "PUT":
            request.user.notifications.active().mark_all_as_unread()
            return Response(status=status.HTTP_200_OK)
        elif request.method == "DELETE":
            request.user.notifications.active().mark_all_as_deleted()
            return Response(status=status.HTTP_204_NO_CONTENT)
        

        
    def retrieve(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.mark_as_read()
        serilaizer = self.serializer_class(notification)
        return Response(serilaizer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.mark_as_unread()
        serilaizer = self.serializer_class(notification)
        return Response(serilaizer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        notification = self.get_object()
        self.perform_destroy(notification)
        return Response(status=status.HTTP_204_NO_CONTENT)


    def get_queryset(self):
        return self.request.user.notifications.active().order_by("-timestamp")