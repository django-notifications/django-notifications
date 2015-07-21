# Create your views here.
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, render, redirect
from django.template.context import RequestContext

from .utils import slug2id
from .models import Notification

from django import get_version
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
        return HttpResponse(json.dumps(data, default=date_handler), content_type="application/json")

@login_required
def all(request):
    """
    Index page for authenticated user
    """
    if getattr(settings, 'NOTIFICATIONS_SOFT_DELETE', False):
        qs = request.user.notifications.active()
    else:
        qs = request.user.notifications.all()
    return render(request, 'notifications/list.html', {
        'notifications': qs
    })
    actions = request.user.notifications.all()

    paginator = Paginator(actions, 16) # Show 16 notifications per page
    page = request.GET.get('p')

    try:
        action_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        action_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        action_list = paginator.page(paginator.num_pages)

    return render_to_response('notifications/list.html', {
        'member': request.user,
        'action_list': action_list,
    }, context_instance=RequestContext(request))

@login_required
def unread(request):
    return render(request, 'notifications/list.html', {
        'notifications': request.user.notifications.unread()
    })

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

    notification = get_object_or_404(Notification, recipient=request.user, id=id)
    notification.mark_as_read()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)

    return redirect('notifications:all')

@login_required
def mark_as_unread(request, slug=None):
    id = slug2id(slug)

    notification = get_object_or_404(Notification, recipient=request.user, id=id)
    notification.mark_as_unread()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)

    return redirect('notifications:all')


@login_required
def delete(request, slug=None):
    _id = slug2id(slug)

    notification = get_object_or_404(Notification, recipient=request.user, id=_id)
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
    from random import randint
    data = {
       'unread_count':request.user.notifications.unread().count(),
    }
    return JsonResponse(data)

def live_unread_notification_list(request):
    
    try:
        num_to_fetch = request.GET.get('max',5) #If they don't specify, make it 5.
        num_to_fetch = int(num_to_fetch)
        num_to_fetch = max(1,num_to_fetch) # if num_to_fetch is negative, force at least one fetched notifications
        num_to_fetch = min(num_to_fetch,100) # put a sane ceiling on the number retrievable 
    except ValueError:
        num_to_fetch = 5 # If casting to an int fails, just make it 5.

    data = {
       'unread_count':request.user.notifications.unread().count(),
       'unread_list':[model_to_dict(n) for n in request.user.notifications.unread()[0:num_to_fetch]]
    }
    return JsonResponse(data)

