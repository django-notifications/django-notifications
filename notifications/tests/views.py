from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from notifications import notify
import random

def live_tester(request):
    notify.send(sender=request.user, recipient=request.user, verb='you loaded the page')

    data = {
        'unread_count': request.user.notifications.unread().count(),
        'notifications': request.user.notifications.all()
    }
    return render(request,'test_live.html',data)
    
def make_notification(request):

    the_notification = random.choice([
        'reticulating splines',
        'cleaning the car',
        'jumping the shark',
        'testing the app',
        ])

    notify.send(sender=request.user, recipient=request.user, verb='you asked for a notification - you are '+the_notification)

