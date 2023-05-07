import os
from unittest import skipUnless

import swapper
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
