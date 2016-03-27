from django.shortcuts import render

from notifications import notify
import random


def live_tester(request):
    notify.send(sender=request.user, recipient=request.user, verb='you loaded the page')

    return render(request, 'test_live.html', {
        'unread_count': request.user.notifications.unread().count(),
        'notifications': request.user.notifications.all()
    })


def make_notification(request):

    the_notification = random.choice([
        'reticulating splines',
        'cleaning the car',
        'jumping the shark',
        'testing the app',
        'attaching the plumbus',
    ])

    notify.send(sender=request.user, recipient=request.user,
                verb='you asked for a notification - you are ' + the_notification)
