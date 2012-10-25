# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render, redirect
from django.template.context import RequestContext
from .utils import slug2id
from notifications.models import Notification

@login_required
def all(request):
    """
    Index page for authenticated user
    """
    return render(request, 'notifications/list.html', {
        'notifications': request.user.notifications.all()
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
    return redirect('notifications:all')

@login_required
def mark_as_read(request, slug=None):
    id = slug2id(slug)

    notification = get_object_or_404(Notification, recipient=request.user, id=id)
    notification.mark_as_read()

    next = request.REQUEST.get('next')

    if next:
        return redirect(next)

    return redirect('notifications:all')
