# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils import timezone
# from django.test.testcases import TestCase
from rest_framework.test import APITestCase

from rest_framework import status
from rest_framework.authtoken.models import Token

from notifications.drf.tests.factories import UserFactory, NotificationFactory


class NotificationViewSetTests(APITestCase):
    def _login(self, user):
        # Create token for user
        token, created = Token.objects.get_or_create(user=user)

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_create_notification(self):
        """
        Test creating a notification.
        """
        # create user
        user = UserFactory()
        self._login(user=user)

        # perform request
        result = self.client.post(reverse('notifications:api:notifications-list'))

        # Check result
        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # perform request
        result = self.client.get(reverse('notifications:api:notifications-list'))

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['count'], 0)

        # create some notifications
        [NotificationFactory(recipient=user) for i in range(10)]
        [NotificationFactory() for i in range(10)]

        # perform request
        result = self.client.get(reverse('notifications:api:notifications-list'))

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['count'], 10)

    def test_get_notification(self):
        # create user
        user = UserFactory()
        self._login(user=user)

        # generate notifications
        notifications = [NotificationFactory(recipient=user) for i in range(5)]

        # perform request
        result = self.client.get(
            reverse(
                'notifications:api:notifications-detail',
                kwargs={'pk': notifications[0].pk}
            )
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['id'], notifications[0].id)
        self.assertEqual(result.data['verb'], notifications[0].verb)
        self.assertEqual(result.data['description'], notifications[0].description)
        self.assertEqual(result.data['recipient']['id'], notifications[0].recipient.id)

        # perform request
        result = self.client.patch(
            reverse(
                'notifications:api:notifications-detail',
                kwargs={'pk': notifications[0].pk}
            ),
            {}
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # perform request
        result = self.client.put(
            reverse(
                'notifications:api:notifications-detail',
                kwargs={'pk': notifications[0].pk}
            ),
            {}
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # test mark as read
    def test_mark_as_read(self):
        # create user
        user = UserFactory()
        self._login(user=user)

        # generate notifications
        notifications = [NotificationFactory(recipient=user) for i in range(5)]

        # perform request
        result = self.client.post(
            reverse(
                'notifications:api:notifications-mark-as-read',
                kwargs={'pk': notifications[0].pk}
            )
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['id'], notifications[0].id)
        self.assertIsNotNone(result.data['read_at'])
        self.assertIsNone(result.data['archived_at'])

    # test mark as unread
    def test_mark_as_unread(self):
        # create user
        user = UserFactory()
        self._login(user=user)

        # generate notifications
        notifications = [NotificationFactory(recipient=user) for i in range(5)]

        # perform request
        result = self.client.post(
            reverse(
                'notifications:api:notifications-mark-as-unread',
                kwargs={'pk': notifications[0].pk}
            )
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['id'], notifications[0].id)
        self.assertIsNone(result.data['read_at'])
        self.assertIsNone(result.data['archived_at'])

    # test mark as seen
    def test_mark_as_seen(self):
        # create user
        user = UserFactory()
        self._login(user=user)

        # generate notifications
        notifications = [NotificationFactory(recipient=user) for i in range(5)]

        # perform request
        result = self.client.post(
            reverse(
                'notifications:api:notifications-mark-as-seen',
                kwargs={'pk': notifications[0].pk}
            )
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['id'], notifications[0].id)
        self.assertIsNotNone(result.data['seen_at'])
        self.assertIsNone(result.data['archived_at'])

    # test mark as unseen
    def test_mark_as_unseen(self):
        # create user
        user = UserFactory()
        self._login(user=user)

        # generate notifications
        notifications = [NotificationFactory(recipient=user) for i in range(5)]

        # perform request
        result = self.client.post(
            reverse(
                'notifications:api:notifications-mark-as-unseen',
                kwargs={'pk': notifications[0].pk}
            )
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['id'], notifications[0].id)
        self.assertIsNone(result.data['seen_at'])
        self.assertIsNone(result.data['archived_at'])

    # test mark all as read
    def test_mark_all_as_read(self):
        # create user
        user = UserFactory()
        self._login(user=user)

        # generate notifications
        [NotificationFactory(recipient=user) for i in range(5)]

        # perform request
        result = self.client.post(
            reverse(
                'notifications:api:notifications-mark-all-as-read',
            )
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIsNone(result.data)

        # perform request
        result = self.client.get(
            reverse(
                'notifications:api:notifications-list',
            )
        )

        # check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['count'], 5)
        for res in result.data['results']:
            self.assertIsNotNone(res['read_at'])

    # test mark all as unread
    def test_mark_all_as_unread(self):
        # create user
        user = UserFactory()
        self._login(user=user)

        # generate notifications
        [NotificationFactory(recipient=user, read_at=timezone.now()) for i in range(5)]

        # perform request
        result = self.client.post(
            reverse(
                'notifications:api:notifications-mark-all-as-unread',
            )
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIsNone(result.data)

        # perform request
        result = self.client.get(
            reverse(
                'notifications:api:notifications-list',
            )
        )

        # check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['count'], 5)
        for res in result.data['results']:
            self.assertIsNone(res['read_at'])

    # test mark all as seen
    def test_mark_all_as_seen(self):
        # create user
        user = UserFactory()
        self._login(user=user)

        # generate notifications
        [NotificationFactory(recipient=user) for i in range(5)]

        # perform request
        result = self.client.post(
            reverse(
                'notifications:api:notifications-mark-all-as-seen',
            )
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIsNone(result.data)

        # perform request
        result = self.client.get(
            reverse(
                'notifications:api:notifications-list',
            )
        )

        # check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['count'], 5)
        for res in result.data['results']:
            self.assertIsNotNone(res['seen_at'])

    # test mark all as unseen
    def test_mark_all_as_unseen(self):
        # create user
        user = UserFactory()
        self._login(user=user)

        # generate notifications
        [NotificationFactory(recipient=user, seen_at=timezone.now()) for i in range(5)]

        # perform request
        result = self.client.post(
            reverse(
                'notifications:api:notifications-mark-all-as-unseen',
            )
        )

        # Check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIsNone(result.data)

        # perform request
        result = self.client.get(
            reverse(
                'notifications:api:notifications-list',
            )
        )

        # check result
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data['count'], 5)
        for res in result.data['results']:
            self.assertIsNone(res['seen_at'])
