"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
Replace this with more appropriate tests for your application.
"""
from django.test import TestCase, RequestFactory
try:
    # Django >= 1.7
    from django.test import override_settings
except ImportError:
    # Django <= 1.6
    from django.test.utils import override_settings

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils.timezone import utc, localtime
from django.utils import timezone
import pytz
import json

from notifications import notify
from notifications.models import Notification
from notifications.utils import id2slug


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
        self.message_count = 10
        self.from_user = User.objects.create(username="from2", password="pwd", email="example@example.com")
        self.to_user = User.objects.create(username="to2", password="pwd", email="example@example.com")
        for i in range(self.message_count):
            notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)

    def test_unread_manager(self):
        self.assertEqual(Notification.objects.unread().count(), self.message_count)
        n = Notification.objects.filter(recipient=self.to_user).first()
        n.mark_as_read()
        self.assertEqual(Notification.objects.unread().count(), self.message_count-1)
        for n in Notification.objects.unread():
            self.assertTrue(n.unread)

    def test_read_manager(self):
        self.assertEqual(Notification.objects.unread().count(), self.message_count)
        n = Notification.objects.filter(recipient=self.to_user).first()
        n.mark_as_read()
        self.assertEqual(Notification.objects.read().count(),1)
        for n in Notification.objects.read():
            self.assertFalse(n.unread)

    def test_mark_all_as_read_manager(self):
        self.assertEqual(Notification.objects.unread().count(), self.message_count)
        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        self.assertEqual(Notification.objects.unread().count(),0)

    def test_mark_all_as_unread_manager(self):
        self.assertEqual(Notification.objects.unread().count(), self.message_count)
        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        self.assertEqual(Notification.objects.unread().count(),0)
        Notification.objects.filter(recipient=self.to_user).mark_all_as_unread()
        self.assertEqual(Notification.objects.unread().count(), self.message_count)

    def test_mark_all_deleted_manager_without_soft_delete(self):
        self.assertRaises(ImproperlyConfigured, Notification.objects.active)
        self.assertRaises(ImproperlyConfigured, Notification.objects.active)
        self.assertRaises(ImproperlyConfigured, Notification.objects.mark_all_as_deleted)
        self.assertRaises(ImproperlyConfigured, Notification.objects.mark_all_as_active)

    @override_settings(NOTIFICATIONS_SOFT_DELETE=True)
    def test_mark_all_deleted_manager(self):
        n = Notification.objects.filter(recipient=self.to_user).first()
        n.mark_as_read()
        self.assertEqual(Notification.objects.read().count(), 1)
        self.assertEqual(Notification.objects.unread().count(), self.message_count-1)
        self.assertEqual(Notification.objects.active().count(), self.message_count)
        self.assertEqual(Notification.objects.deleted().count(), 0)

        Notification.objects.mark_all_as_deleted()
        self.assertEqual(Notification.objects.read().count(), 0)
        self.assertEqual(Notification.objects.unread().count(), 0)
        self.assertEqual(Notification.objects.active().count(), 0)
        self.assertEqual(Notification.objects.deleted().count(), self.message_count)

        Notification.objects.mark_all_as_active()
        self.assertEqual(Notification.objects.read().count(), 1)
        self.assertEqual(Notification.objects.unread().count(), self.message_count-1)
        self.assertEqual(Notification.objects.active().count(), self.message_count)
        self.assertEqual(Notification.objects.deleted().count(), 0)


class NotificationTestPages(TestCase):

    def setUp(self):
        self.message_count = 10
        self.from_user = User.objects.create_user(username="from", password="pwd", email="example@example.com")
        self.to_user = User.objects.create_user(username="to", password="pwd", email="example@example.com")
        self.to_user.is_staff = True
        self.to_user.save()
        for i in range(self.message_count):
            notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)

    def logout(self):
        self.client.post(reverse('admin:logout')+'?next=/', {})

    def login(self,username,password):
        self.logout()
        response = self.client.post(reverse('login'), {'username': username, 'password': password})
        self.assertEqual(response.status_code,302)
        return response

    def test_all_messages_page(self):
        self.login('to','pwd')
        response = self.client.get(reverse('notifications:all'))

        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context['notifications']),len(self.to_user.notifications.all()))

    def test_unread_messages_pages(self):
        self.login('to','pwd')
        response = self.client.get(reverse('notifications:unread'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context['notifications']),len(self.to_user.notifications.unread()))
        self.assertEqual(len(response.context['notifications']), self.message_count)

        for i,n in enumerate(self.to_user.notifications.all()):
            if i%3 == 0:
                response = self.client.get(reverse('notifications:mark_as_read',args=[id2slug(n.id)]))
                self.assertEqual(response.status_code,302)

        response = self.client.get(reverse('notifications:unread'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context['notifications']),len(self.to_user.notifications.unread()))
        self.assertTrue(len(response.context['notifications']) < self.message_count)

        response = self.client.get(reverse('notifications:mark_all_as_read'))
        self.assertRedirects(response,reverse('notifications:all'))
        response = self.client.get(reverse('notifications:unread'))
        self.assertEqual(len(response.context['notifications']),len(self.to_user.notifications.unread()))
        self.assertEqual(len(response.context['notifications']),0)

    def test_next_pages(self):
        self.login('to','pwd')
        response = self.client.get(reverse('notifications:mark_all_as_read')+"?next="+reverse('notifications:unread'))
        self.assertRedirects(response,reverse('notifications:unread'))

        slug = id2slug(self.to_user.notifications.first().id)
        response = self.client.get(reverse('notifications:mark_as_read',args=[slug])+"?next="+reverse('notifications:unread'))
        self.assertRedirects(response,reverse('notifications:unread'))

        slug = id2slug(self.to_user.notifications.first().id)
        response = self.client.get(reverse('notifications:mark_as_unread',args=[slug])+"?next="+reverse('notifications:unread'))
        self.assertRedirects(response,reverse('notifications:unread'))

    def test_delete_messages_pages(self):
        self.login('to', 'pwd')

        slug = id2slug(self.to_user.notifications.first().id)
        response = self.client.get(reverse('notifications:delete', args=[slug]))
        self.assertRedirects(response, reverse('notifications:all'))

        response = self.client.get(reverse('notifications:all'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), len(self.to_user.notifications.all()))
        self.assertEqual(len(response.context['notifications']), self.message_count-1)

        response = self.client.get(reverse('notifications:unread'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), len(self.to_user.notifications.unread()))
        self.assertEqual(len(response.context['notifications']), self.message_count-1)

    @override_settings(NOTIFICATIONS_SOFT_DELETE=True)
    def test_soft_delete_messages_manager(self):
        self.login('to', 'pwd')

        slug = id2slug(self.to_user.notifications.first().id)
        response = self.client.get(reverse('notifications:delete', args=[slug]))
        self.assertRedirects(response, reverse('notifications:all'))

        response = self.client.get(reverse('notifications:all'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), len(self.to_user.notifications.active()))
        self.assertEqual(len(response.context['notifications']), self.message_count-1)

        response = self.client.get(reverse('notifications:unread'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), len(self.to_user.notifications.unread()))
        self.assertEqual(len(response.context['notifications']), self.message_count-1)


    def test_unread_count_api(self):
        self.login('to', 'pwd')

        response = self.client.get(reverse('notifications:live_unread_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()),['unread_count'])
        self.assertEqual(data['unread_count'],10)


        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        response = self.client.get(reverse('notifications:live_unread_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()),['unread_count'])
        self.assertEqual(data['unread_count'],0)

        notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        response = self.client.get(reverse('notifications:live_unread_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()),['unread_count'])
        self.assertEqual(data['unread_count'],1)

    def test_unread_list_api(self):
        self.login('to', 'pwd')

        response = self.client.get(reverse('notifications:live_unread_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())),['unread_count','unread_list'])
        self.assertEqual(data['unread_count'],10)
        self.assertEqual(len(data['unread_list']),5)

        response = self.client.get(reverse('notifications:live_unread_notification_list')+"?max=12")
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())),['unread_count','unread_list'])
        self.assertEqual(data['unread_count'],10)
        self.assertEqual(len(data['unread_list']),10)

        # Test with a bad 'max' value
        response = self.client.get(reverse('notifications:live_unread_notification_list')+"?max=this_is_wrong")
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())),['unread_count','unread_list'])
        self.assertEqual(data['unread_count'],10)
        self.assertEqual(len(data['unread_list']),5)

        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        response = self.client.get(reverse('notifications:live_unread_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())),['unread_count','unread_list'])
        self.assertEqual(data['unread_count'],0)
        self.assertEqual(len(data['unread_list']),0)

        notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        response = self.client.get(reverse('notifications:live_unread_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())),['unread_count','unread_list'])
        self.assertEqual(data['unread_count'],1)
        self.assertEqual(len(data['unread_list']),1)
        self.assertEqual(data['unread_list'][0]['verb'],'commented')

    def test_live_update_tags(self):
        from django.shortcuts import render

        self.login('to', 'pwd')
        self.factory = RequestFactory()

        request = self.factory.get('/notification/live_updater')
        request.user = self.to_user

        page = render(request, 'notifications/test_tags.html', {'request':request})
        
        #TODO: Add more tests to check what is being output.        
