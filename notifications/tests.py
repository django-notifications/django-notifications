"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime

from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import utc


from notifications import notify
from notifications.models import Notification


class NotificationTest(TestCase):

    def setUp(self):
        settings.USE_TZ = True

    @override_settings(USE_TZ=True)
    @override_settings(TIME_ZONE='Asia/Shanghai')
    def test_use_timezone(self):
        from_user = User.objects.create(username="from", password="pwd", email="example@example.com")
        to_user = User.objects.create(username="to", password="pwd", email="example@example.com")
        notify.send(from_user, recipient=to_user, verb='commented', action_object=from_user)
        notification = Notification.objects.get(recipient=to_user)
        delta = datetime.datetime.utcnow().replace(tzinfo=utc) - notification.timestamp
        self.assertTrue(delta.seconds >= 8 * 60 * 59)

    @override_settings(USE_TZ=False)
    @override_settings(TIME_ZONE='Asia/Shanghai')
    def test_disable_timezone(self):
        from_user = User.objects.create(username="from2", password="pwd", email="example@example.com")
        to_user = User.objects.create(username="to2", password="pwd", email="example@example.com")
        notify.send(from_user, recipient=to_user, verb='commented', action_object=from_user)
        notification = Notification.objects.get(recipient=to_user)
        delta = datetime.datetime.utcnow() - notification.timestamp
        self.assertTrue(delta.seconds < 60)
