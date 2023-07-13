import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from swapper import load_model

from notifications.tests.factories.notifications import NotificationFactory
from notifications.tests.factories.users import Recipient

Notification = load_model("notifications", "Notification")
User = get_user_model()


@pytest.mark.parametrize(
    "emailed,method",
    (
        (True, Notification.objects.sent),
        (False, Notification.objects.unsent),
    ),
)
@pytest.mark.django_db
def test_sent_unsent_methods(emailed, method):
    NotificationFactory.create_batch(3, emailed=emailed)
    assert method().count() == 3

    first_notification = Notification.objects.first()
    first_notification.emailed = not emailed
    first_notification.save()
    assert method().count() == 2

    Notification.objects.all().update(emailed=not emailed)
    assert method().count() == 0

    first_notification.emailed = emailed
    first_notification.save()
    assert method().count() == 1


@pytest.mark.parametrize(
    "read,method",
    (
        (False, Notification.objects.read),
        (True, Notification.objects.unread),
    ),
)
@pytest.mark.django_db
def test_query_read_unread_methods(read, method):
    NotificationFactory.create_batch(3, unread=read)
    assert method().count() == 3

    first_notification = Notification.objects.first()
    first_notification.unread = not read
    first_notification.save()
    assert method().count() == 2

    Notification.objects.all().update(unread=not read)
    assert method().count() == 0

    first_notification.unread = read
    first_notification.save()
    assert method().count() == 1


@pytest.mark.parametrize(
    "read,method",
    (
        (False, Notification.objects.read),
        (True, Notification.objects.unread),
    ),
)
@override_settings(NOTIFICATION_SETTINGS={"SOFT_DELETE": True})
@pytest.mark.django_db
def test_query_read_unread_with_deleted_notifications(read, method):
    NotificationFactory.create_batch(3, unread=read)
    assert method().count() == 3

    first_notification = Notification.objects.first()
    first_notification.deleted = True
    first_notification.save()

    assert method().count() == 2
    assert method(include_deleted=True).count() == 3


@pytest.mark.parametrize(
    "status,method,check_method",
    (
        (True, Notification.objects.mark_all_as_read, Notification.objects.read),
        (False, Notification.objects.mark_all_as_unread, Notification.objects.unread),
    ),
)
@pytest.mark.django_db
def test_mark_all_as_read_unread(status, method, check_method):
    NotificationFactory.create_batch(3, unread=status)
    assert check_method().count() == 0

    method()
    assert check_method().count() == 3


@pytest.mark.parametrize(
    "status,method,check_method",
    (
        (True, Notification.objects.mark_all_as_read, Notification.objects.read),
        (False, Notification.objects.mark_all_as_unread, Notification.objects.unread),
    ),
)
@pytest.mark.django_db
def test_mark_all_as_read_unread_with_recipient(status, method, check_method):
    recipient = Recipient()
    NotificationFactory.create_batch(2, unread=status, recipient=recipient)
    NotificationFactory.create_batch(1, unread=status)
    assert Notification.objects.count() == 3
    assert check_method().count() == 0

    method(recipient=recipient)
    assert check_method().count() == 2
