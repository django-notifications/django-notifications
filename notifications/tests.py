"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
Replace this with more appropriate tests for your application.
"""
from django.test import TestCase, override_settings
#from django.test.utils import override_settings
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import utc, localtime
from django.utils import timezone
import pytz

from notifications import notify
from notifications.models import Notification


class NotificationTest(TestCase):

    @override_settings(USE_TZ=True)
    @override_settings(TIME_ZONE='Asia/Shanghai')
    def test_use_timezone(self):
        from_user = User.objects.create(username="from", password="pwd", email="example@example.com")
        to_user = User.objects.create(username="to", password="pwd", email="example@example.com")
        notify.send(from_user, recipient=to_user, verb='commented', action_object=from_user)
        notification = Notification.objects.get(recipient=to_user)
        delta = timezone.now().replace(tzinfo=utc) - localtime(notification.timestamp,pytz.timezone(settings.TIME_ZONE))
        self.assertTrue(delta.seconds < 60)
        # The delta between the two events will still be less than a second despite the different timezones
        # The call to now and the immediate call afterwards will be within a short period of time, not 8 hours as the test above was originally.

    @override_settings(USE_TZ=False)
    @override_settings(TIME_ZONE='Asia/Shanghai')
    def test_disable_timezone(self):
        from_user = User.objects.create(username="from2", password="pwd", email="example@example.com")
        to_user = User.objects.create(username="to2", password="pwd", email="example@example.com")
        notify.send(from_user, recipient=to_user, verb='commented', action_object=from_user)
        notification = Notification.objects.get(recipient=to_user)
        delta = timezone.now() - notification.timestamp
        self.assertTrue(delta.seconds < 60)
        
class NotificationManagersTest(TestCase):
    def setUp(self):

        self.from_user = User.objects.create(username="from2", password="pwd", email="example@example.com")
        self.to_user = User.objects.create(username="to2", password="pwd", email="example@example.com")
        for i in range(10):
            notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        
    def test_unread_manager(self):
        self.assertEqual(Notification.objects.unread().count(),10)
        n = Notification.objects.filter(recipient=self.to_user).first()
        n.mark_as_read()
        self.assertEqual(Notification.objects.unread().count(),9)
        for n in Notification.objects.unread():
            self.assertTrue(n.unread)

    def test_read_manager(self):
        self.assertEqual(Notification.objects.unread().count(),10)
        n = Notification.objects.filter(recipient=self.to_user).first()
        n.mark_as_read()
        self.assertEqual(Notification.objects.read().count(),1)
        for n in Notification.objects.read():
            self.assertFalse(n.unread)
        
    def test_mark_all_as_read_manager(self):
        self.assertEqual(Notification.objects.unread().count(),10)
        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        self.assertEqual(Notification.objects.unread().count(),0)
        
    def test_mark_all_as_unread_manager(self):
        self.assertEqual(Notification.objects.unread().count(),10)
        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        self.assertEqual(Notification.objects.unread().count(),0)
        Notification.objects.filter(recipient=self.to_user).mark_all_as_unread()
        self.assertEqual(Notification.objects.unread().count(),10)
