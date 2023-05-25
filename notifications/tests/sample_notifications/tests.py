import os
from unittest import skipUnless

from django.contrib.auth.models import User
import swapper

from notifications.signals import notify
from notifications.tests.tests import AdminTest as BaseAdminTest
from notifications.tests.tests import NotificationTest as BaseNotificationTest

Notification = swapper.load_model('notifications', 'Notification')


@skipUnless(os.environ.get('SAMPLE_APP', False), 'Running tests on standard django-notifications models')
class AdminTest(BaseAdminTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        BaseAdminTest.app_name = 'sample_notifications'


@skipUnless(os.environ.get('SAMPLE_APP', False), 'Running tests on standard django-notifications models')
class NotificationTest(BaseNotificationTest):
    pass


class TestExtraDataCustomAccessor(NotificationTest):
    def setUp(self):
        self.from_user = User.objects.create_user(username="from_extra", password="pwd", email="example@example.com")
        self.to_user = User.objects.create_user(username="to_extra", password="pwd", email="example@example.com")
        notify.send(
            self.from_user,
            recipient=self.to_user,
            verb='commented',
            action_object=self.from_user,
            url="/learn/ask-a-pro/q/test-question-9/299/",
            other_content="Hello my 'world'",
            details="test detail"
        )

    def test_extra_data(self):
        notification = Notification.objects.get(details="test detail")
        assert notification, "Expected a notification retrieved by custom extra data accessor"
        assert notification.details == "test detail", "Custom accessor should return set value"
        assert "details" not in notification.data, "Custom accessor should not be in json data"
