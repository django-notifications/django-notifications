'''
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
Replace this with more appropriate tests for your application.
'''
# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines,missing-docstring
import json

import pytz

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.template import Context, Template
from django.test import Client, RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from django.utils.timezone import localtime, utc
from notifications.base.models import notify_handler
from notifications.signals import notify
from notifications.utils import id2slug
from swapper import load_model

Notification = load_model('notifications', 'Notification')

try:
    # Django >= 1.7
    from django.test import override_settings  # noqa
except ImportError:
    # Django <= 1.6
    from django.test.utils import override_settings  # noqa

try:
    # Django >= 1.7
    from django.urls import reverse
except ImportError:
    # Django <= 1.6
    from django.core.urlresolvers import reverse  # pylint: disable=no-name-in-module,import-error

MALICIOUS_NEXT_URLS = [
    "http://bla.com",
    "http://www.bla.com",
    "https://bla.com",
    "https://www.bla.com",
    "ftp://www.bla.com/file.exe",
]

class NotificationTest(TestCase):
    ''' Django notifications automated tests '''
    @override_settings(USE_TZ=True)
    @override_settings(TIME_ZONE='Asia/Shanghai')
    def test_use_timezone(self):
        from_user = User.objects.create(username="from", password="pwd", email="example@example.com")
        to_user = User.objects.create(username="to", password="pwd", email="example@example.com")
        notify.send(from_user, recipient=to_user, verb='commented', action_object=from_user)
        notification = Notification.objects.get(recipient=to_user)
        delta = (
            timezone.now().replace(tzinfo=utc) - localtime(notification.timestamp, pytz.timezone(settings.TIME_ZONE))
        )
        self.assertTrue(delta.seconds < 60)
        # The delta between the two events will still be less than a second despite the different timezones
        # The call to now and the immediate call afterwards will be within a short period of time, not 8 hours as the
        # test above was originally.

    @override_settings(USE_TZ=False)
    @override_settings(TIME_ZONE='Asia/Shanghai')
    def test_disable_timezone(self):
        from_user = User.objects.create(username="from2", password="pwd", email="example@example.com")
        to_user = User.objects.create(username="to2", password="pwd", email="example@example.com")
        notify.send(from_user, recipient=to_user, verb='commented', action_object=from_user)
        notification = Notification.objects.get(recipient=to_user)
        delta = timezone.now() - notification.timestamp
        self.assertTrue(delta.seconds < 60)

    def test_humanize_naturalday_timestamp(self):
        from_user = User.objects.create(username="from2", password="pwd", email="example@example.com")
        to_user = User.objects.create(username="to2", password="pwd", email="example@example.com")
        notify.send(from_user, recipient=to_user, verb='commented', action_object=from_user)
        notification = Notification.objects.get(recipient=to_user)
        self.assertEqual(notification.naturalday(), 'today')

    def test_humanize_naturaltime_timestamp(self):
        from_user = User.objects.create(username="from2", password="pwd", email="example@example.com")
        to_user = User.objects.create(username="to2", password="pwd", email="example@example.com")
        notify.send(from_user, recipient=to_user, verb='commented', action_object=from_user)
        notification = Notification.objects.get(recipient=to_user)
        self.assertEqual(notification.naturaltime(), 'now')

class NotificationManagersTest(TestCase):
    ''' Django notifications Manager automated tests '''
    def setUp(self):
        self.message_count = 10
        self.other_user = User.objects.create(username="other1", password="pwd", email="example@example.com")

        self.from_user = User.objects.create(username="from2", password="pwd", email="example@example.com")
        self.to_user = User.objects.create(username="to2", password="pwd", email="example@example.com")
        self.to_group = Group.objects.create(name="to2_g")
        self.to_user_list = User.objects.all()
        self.to_group.user_set.add(self.to_user)
        self.to_group.user_set.add(self.other_user)

        for _ in range(self.message_count):
            notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        # Send notification to group
        notify.send(self.from_user, recipient=self.to_group, verb='commented', action_object=self.from_user)
        self.message_count += self.to_group.user_set.count()
        # Send notification to user list
        notify.send(self.from_user, recipient=self.to_user_list, verb='commented', action_object=self.from_user)
        self.message_count += len(self.to_user_list)

    def test_notify_send_return_val(self):
        results = notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        for result in results:
            if result[0] is notify_handler:
                self.assertEqual(len(result[1]), 1)
                # only check types for now
                self.assertEqual(type(result[1][0]), Notification)

    def test_notify_send_return_val_group(self):  # pylint: disable=invalid-name
        results = notify.send(self.from_user, recipient=self.to_group, verb='commented', action_object=self.from_user)
        for result in results:
            if result[0] is notify_handler:
                self.assertEqual(len(result[1]), self.to_group.user_set.count())
                for notification in result[1]:
                    # only check types for now
                    self.assertEqual(type(notification), Notification)

    def test_unread_manager(self):
        self.assertEqual(Notification.objects.unread().count(), self.message_count)
        notification = Notification.objects.filter(recipient=self.to_user).first()
        notification.mark_as_read()
        self.assertEqual(Notification.objects.unread().count(), self.message_count-1)
        for notification in Notification.objects.unread():
            self.assertTrue(notification.unread)

    def test_read_manager(self):
        self.assertEqual(Notification.objects.unread().count(), self.message_count)
        notification = Notification.objects.filter(recipient=self.to_user).first()
        notification.mark_as_read()
        self.assertEqual(Notification.objects.read().count(), 1)
        for notification in Notification.objects.read():
            self.assertFalse(notification.unread)

    def test_mark_all_as_read_manager(self):
        self.assertEqual(Notification.objects.unread().count(), self.message_count)
        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        self.assertEqual(self.to_user.notifications.unread().count(), 0)

    @override_settings(DJANGO_NOTIFICATIONS_CONFIG={
        'SOFT_DELETE': True
    })  # pylint: disable=invalid-name
    def test_mark_all_as_read_manager_with_soft_delete(self):
        # even soft-deleted notifications should be marked as read
        # refer: https://github.com/django-notifications/django-notifications/issues/126
        to_delete = Notification.objects.filter(recipient=self.to_user).order_by('id')[0]
        to_delete.deleted = True
        to_delete.save()
        self.assertTrue(Notification.objects.filter(recipient=self.to_user).order_by('id')[0].unread)
        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        self.assertFalse(Notification.objects.filter(recipient=self.to_user).order_by('id')[0].unread)

    def test_mark_all_as_unread_manager(self):
        self.assertEqual(Notification.objects.unread().count(), self.message_count)
        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        self.assertEqual(self.to_user.notifications.unread().count(), 0)
        Notification.objects.filter(recipient=self.to_user).mark_all_as_unread()
        self.assertEqual(Notification.objects.unread().count(), self.message_count)

    def test_mark_all_deleted_manager_without_soft_delete(self):  # pylint: disable=invalid-name
        self.assertRaises(ImproperlyConfigured, Notification.objects.active)
        self.assertRaises(ImproperlyConfigured, Notification.objects.active)
        self.assertRaises(ImproperlyConfigured, Notification.objects.mark_all_as_deleted)
        self.assertRaises(ImproperlyConfigured, Notification.objects.mark_all_as_active)

    @override_settings(DJANGO_NOTIFICATIONS_CONFIG={
        'SOFT_DELETE': True
    })
    def test_mark_all_deleted_manager(self):
        notification = Notification.objects.filter(recipient=self.to_user).first()
        notification.mark_as_read()
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
    ''' Django notifications automated page tests '''
    def setUp(self):
        self.message_count = 10
        self.from_user = User.objects.create_user(username="from", password="pwd", email="example@example.com")
        self.to_user = User.objects.create_user(username="to", password="pwd", email="example@example.com")
        self.to_user.is_staff = True
        self.to_user.save()
        for _ in range(self.message_count):
            notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)

    def logout(self):
        self.client.post(reverse('admin:logout')+'?next=/', {})

    def login(self, username, password):
        self.logout()
        response = self.client.post(reverse('login'), {'username': username, 'password': password})
        self.assertEqual(response.status_code, 302)
        return response

    def test_all_messages_page(self):
        self.login('to', 'pwd')
        response = self.client.get(reverse('notifications:all'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), len(self.to_user.notifications.all()))

    def test_unread_messages_pages(self):
        self.login('to', 'pwd')
        response = self.client.get(reverse('notifications:unread'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), len(self.to_user.notifications.unread()))
        self.assertEqual(len(response.context['notifications']), self.message_count)

        for index, notification in enumerate(self.to_user.notifications.all()):
            if index % 3 == 0:
                response = self.client.get(reverse('notifications:mark_as_read', args=[id2slug(notification.id)]))
                self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('notifications:unread'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), len(self.to_user.notifications.unread()))
        self.assertTrue(len(response.context['notifications']) < self.message_count)

        response = self.client.get(reverse('notifications:mark_all_as_read'))
        self.assertRedirects(response, reverse('notifications:unread'))
        response = self.client.get(reverse('notifications:unread'))
        self.assertEqual(len(response.context['notifications']), len(self.to_user.notifications.unread()))
        self.assertEqual(len(response.context['notifications']), 0)

    def test_next_pages(self):
        self.login('to', 'pwd')
        query_parameters = '?var1=hello&var2=world'

        response = self.client.get(reverse('notifications:mark_all_as_read'),data={
            "next": reverse('notifications:unread')  + query_parameters,
        })
        self.assertRedirects(response, reverse('notifications:unread') + query_parameters)

        slug = id2slug(self.to_user.notifications.first().id)
        response = self.client.get(reverse('notifications:mark_as_read', args=[slug]), data={
            "next": reverse('notifications:unread') + query_parameters,
        })
        self.assertRedirects(response, reverse('notifications:unread') + query_parameters)

        slug = id2slug(self.to_user.notifications.first().id)
        response = self.client.get(reverse('notifications:mark_as_unread', args=[slug]), {
            "next": reverse('notifications:unread') + query_parameters,
        })
        self.assertRedirects(response, reverse('notifications:unread') + query_parameters)

    @override_settings(ALLOWED_HOSTS=["www.notifications.com"])
    def test_malicious_next_pages(self):
        self.client.force_login(self.to_user)
        query_parameters = '?var1=hello&var2=world'

        for next_url in MALICIOUS_NEXT_URLS:
            response = self.client.get(reverse('notifications:mark_all_as_read'),data={
                "next": next_url  + query_parameters,
            })
            self.assertRedirects(response, reverse('notifications:unread'))

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

    @override_settings(DJANGO_NOTIFICATIONS_CONFIG={
        'SOFT_DELETE': True
    })  # pylint: disable=invalid-name
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
        self.assertEqual(list(data.keys()), ['unread_count'])
        self.assertEqual(data['unread_count'], self.message_count)

        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        response = self.client.get(reverse('notifications:live_unread_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()), ['unread_count'])
        self.assertEqual(data['unread_count'], 0)

        notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        response = self.client.get(reverse('notifications:live_unread_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()), ['unread_count'])
        self.assertEqual(data['unread_count'], 1)

    def test_all_count_api(self):
        self.login('to', 'pwd')

        response = self.client.get(reverse('notifications:live_all_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()), ['all_count'])
        self.assertEqual(data['all_count'], self.message_count)

        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        response = self.client.get(reverse('notifications:live_all_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()), ['all_count'])
        self.assertEqual(data['all_count'], self.message_count)

        notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        response = self.client.get(reverse('notifications:live_all_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()), ['all_count'])
        self.assertEqual(data['all_count'], self.message_count + 1)

    def test_unread_list_api(self):
        self.login('to', 'pwd')

        response = self.client.get(reverse('notifications:live_unread_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['unread_count', 'unread_list'])
        self.assertEqual(data['unread_count'], self.message_count)
        self.assertEqual(len(data['unread_list']), self.message_count)

        response = self.client.get(reverse('notifications:live_unread_notification_list'), data={"max": 5})
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['unread_count', 'unread_list'])
        self.assertEqual(data['unread_count'], self.message_count)
        self.assertEqual(len(data['unread_list']), 5)

        # Test with a bad 'max' value
        response = self.client.get(reverse('notifications:live_unread_notification_list'), data={
            "max": "this_is_wrong",
        })
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['unread_count', 'unread_list'])
        self.assertEqual(data['unread_count'], self.message_count)
        self.assertEqual(len(data['unread_list']), self.message_count)

        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        response = self.client.get(reverse('notifications:live_unread_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['unread_count', 'unread_list'])
        self.assertEqual(data['unread_count'], 0)
        self.assertEqual(len(data['unread_list']), 0)

        notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        response = self.client.get(reverse('notifications:live_unread_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['unread_count', 'unread_list'])
        self.assertEqual(data['unread_count'], 1)
        self.assertEqual(len(data['unread_list']), 1)
        self.assertEqual(data['unread_list'][0]['verb'], 'commented')
        self.assertEqual(data['unread_list'][0]['slug'], id2slug(data['unread_list'][0]['id']))

    def test_all_list_api(self):
        self.login('to', 'pwd')

        response = self.client.get(reverse('notifications:live_all_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['all_count', 'all_list'])
        self.assertEqual(data['all_count'], self.message_count)
        self.assertEqual(len(data['all_list']), self.message_count)

        response = self.client.get(reverse('notifications:live_all_notification_list'), data={"max": 5})
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['all_count', 'all_list'])
        self.assertEqual(data['all_count'], self.message_count)
        self.assertEqual(len(data['all_list']), 5)

        # Test with a bad 'max' value
        response = self.client.get(reverse('notifications:live_all_notification_list'), data={
            "max": "this_is_wrong",
        })
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['all_count', 'all_list'])
        self.assertEqual(data['all_count'], self.message_count)
        self.assertEqual(len(data['all_list']), self.message_count)

        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        response = self.client.get(reverse('notifications:live_all_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['all_count', 'all_list'])
        self.assertEqual(data['all_count'], self.message_count)
        self.assertEqual(len(data['all_list']), self.message_count)

        notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        response = self.client.get(reverse('notifications:live_all_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['all_count', 'all_list'])
        self.assertEqual(data['all_count'], self.message_count + 1)
        self.assertEqual(len(data['all_list']), self.message_count)
        self.assertEqual(data['all_list'][0]['verb'], 'commented')
        self.assertEqual(data['all_list'][0]['slug'], id2slug(data['all_list'][0]['id']))

    def test_unread_list_api_mark_as_read(self):  # pylint: disable=invalid-name
        self.login('to', 'pwd')
        num_requested = 3
        response = self.client.get(
            reverse('notifications:live_unread_notification_list'),
            data={"max": num_requested, "mark_as_read": 1}
        )
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['unread_count'],
                         self.message_count - num_requested)
        self.assertEqual(len(data['unread_list']), num_requested)
        response = self.client.get(
            reverse('notifications:live_unread_notification_list'),
            data={"max": num_requested, "mark_as_read": 1}
        )
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['unread_count'],
                         self.message_count - 2*num_requested)
        self.assertEqual(len(data['unread_list']), num_requested)

    def test_live_update_tags(self):
        from django.shortcuts import render

        self.login('to', 'pwd')
        factory = RequestFactory()

        request = factory.get('/notification/live_updater')
        request.user = self.to_user

        render(request, 'notifications/test_tags.html', {'request': request, 'nonce': 'nonce-T5esDNXMnDe5lKMQ6ZzTUw=='})

        # TODO: Add more tests to check what is being output.

    def test_anon_user_gets_nothing(self):
        response = self.client.post(reverse('notifications:live_unread_notification_count'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['unread_count'], 0)

        response = self.client.post(reverse('notifications:live_unread_notification_list'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['unread_count'], 0)
        self.assertEqual(data['unread_list'], [])


class NotificationTestExtraData(TestCase):
    ''' Django notifications automated extra data tests '''
    def setUp(self):
        self.message_count = 1
        self.from_user = User.objects.create_user(username="from", password="pwd", email="example@example.com")
        self.to_user = User.objects.create_user(username="to", password="pwd", email="example@example.com")
        self.to_user.is_staff = True
        self.to_user.save()
        for _ in range(self.message_count):
            notify.send(
                self.from_user,
                recipient=self.to_user,
                verb='commented',
                action_object=self.from_user,
                url="/learn/ask-a-pro/q/test-question-9/299/",
                other_content="Hello my 'world'"
            )

    def logout(self):
        self.client.post(reverse('admin:logout')+'?next=/', {})

    def login(self, username, password):
        self.logout()
        response = self.client.post(reverse('login'), {'username': username, 'password': password})
        self.assertEqual(response.status_code, 302)
        return response

    def test_extra_data(self):
        self.login('to', 'pwd')
        response = self.client.post(reverse('notifications:live_unread_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['unread_list'][0]['data']['url'], "/learn/ask-a-pro/q/test-question-9/299/")
        self.assertEqual(data['unread_list'][0]['data']['other_content'], "Hello my 'world'")


class TagTest(TestCase):
    ''' Django notifications automated tags tests '''
    def setUp(self):
        self.message_count = 1
        self.from_user = User.objects.create_user(username="from", password="pwd", email="example@example.com")
        self.to_user = User.objects.create_user(username="to", password="pwd", email="example@example.com")
        self.to_user.is_staff = True
        self.to_user.save()
        for _ in range(self.message_count):
            notify.send(
                self.from_user,
                recipient=self.to_user,
                verb='commented',
                action_object=self.from_user,
                url="/learn/ask-a-pro/q/test-question-9/299/",
                other_content="Hello my 'world'"
            )

    def tag_test(self, template, context, output):
        t = Template('{% load notifications_tags %}'+template)
        c = Context(context)
        self.assertEqual(t.render(c), output)

    def test_has_notification(self):
        template = "{{ user|has_notification }}"
        context = {"user":self.to_user}
        output = u"True"
        self.tag_test(template, context, output)


class AdminTest(TestCase):
    app_name = "notifications"
    def setUp(self):
        self.message_count = 10
        self.from_user = User.objects.create_user(username="from", password="pwd", email="example@example.com")
        self.to_user = User.objects.create_user(username="to", password="pwd", email="example@example.com")
        self.to_user.is_staff = True
        self.to_user.is_superuser = True
        self.to_user.save()
        for _ in range(self.message_count):
            notify.send(
                self.from_user,
                recipient=self.to_user,
                verb='commented',
                action_object=self.from_user,
            )

    def test_list(self):
        self.client.login(username='to', password='pwd')

        with CaptureQueriesContext(connection=connection) as context:
            response = self.client.get(reverse('admin:{0}_notification_changelist'.format(self.app_name)))
            self.assertLessEqual(len(context), 6)

        self.assertEqual(response.status_code, 200, response.content)
