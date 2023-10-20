import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
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
def test_read_unread_methods(read, method):
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
@override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True})
@pytest.mark.django_db
def test_read_unread_with_deleted_notifications(read, method):
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


@override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True})
@pytest.mark.parametrize(
    "deleted,method",
    (
        (True, Notification.objects.deleted),
        (False, Notification.objects.active),
    ),
)
@pytest.mark.django_db
def test_deleted_active_methods(deleted, method):
    NotificationFactory.create_batch(3, deleted=deleted)
    assert method().count() == 3

    first_notification = Notification.objects.first()
    first_notification.deleted = not deleted
    first_notification.save()
    assert method().count() == 2

    Notification.objects.all().update(deleted=not deleted)
    assert method().count() == 0

    first_notification.deleted = deleted
    first_notification.save()
    assert method().count() == 1


@pytest.mark.parametrize(
    "method",
    (
        Notification.objects.deleted,
        Notification.objects.active,
    ),
)
@pytest.mark.django_db
def test_deleted_active_methods_without_soft_delete(method):
    with pytest.raises(ImproperlyConfigured):
        assert method()


@override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True})
@pytest.mark.parametrize(
    "status,method,check_method",
    (
        (False, Notification.objects.mark_all_as_deleted, Notification.objects.deleted),
        (True, Notification.objects.mark_all_as_active, Notification.objects.active),
    ),
)
@pytest.mark.django_db
def test_mark_all_as_deleted_active(status, method, check_method):
    NotificationFactory.create_batch(3, deleted=status)
    assert Notification.objects.count() == 3
    assert check_method().count() == 0

    method()
    assert check_method().count() == 3


@override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True})
@pytest.mark.parametrize(
    "status,method,check_method",
    (
        (False, Notification.objects.mark_all_as_deleted, Notification.objects.deleted),
        (True, Notification.objects.mark_all_as_active, Notification.objects.active),
    ),
)
@pytest.mark.django_db
def test_mark_all_as_deleted_active_with_recipient(status, method, check_method):
    recipient = Recipient()
    NotificationFactory.create_batch(2, deleted=status, recipient=recipient)
    NotificationFactory.create_batch(1, deleted=status)
    assert Notification.objects.count() == 3
    assert check_method().count() == 0

    method(recipient=recipient)
    assert check_method().count() == 2


@pytest.mark.parametrize(
    "method",
    (
        Notification.objects.mark_all_as_deleted,
        Notification.objects.mark_all_as_active,
    ),
)
@pytest.mark.django_db
def test_mark_all_as_deleted_active_without_soft_delete(method):
    with pytest.raises(ImproperlyConfigured):
        method()


@pytest.mark.parametrize(
    "status,method,check_method",
    (
        (False, Notification.objects.mark_as_sent, Notification.objects.sent),
        (True, Notification.objects.mark_as_unsent, Notification.objects.unsent),
    ),
)
@pytest.mark.django_db
def test_mark_as_sent_unsent_method(status, method, check_method):
    NotificationFactory.create_batch(3, emailed=status)
    assert Notification.objects.count() == 3
    assert check_method().count() == 0

    method()
    assert check_method().count() == 3


@pytest.mark.parametrize(
    "status,method,check_method",
    (
        (False, Notification.objects.mark_as_sent, Notification.objects.sent),
        (True, Notification.objects.mark_as_unsent, Notification.objects.unsent),
    ),
)
@pytest.mark.django_db
def test_mark_as_sent_unsent_with_recipient(status, method, check_method):
    recipient = Recipient()
    NotificationFactory.create_batch(2, emailed=status, recipient=recipient)
    NotificationFactory.create_batch(1, emailed=status)
    assert Notification.objects.count() == 3
    assert check_method().count() == 0

    method(recipient=recipient)
    assert check_method().count() == 2
