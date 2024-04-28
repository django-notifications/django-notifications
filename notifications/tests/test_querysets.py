import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from swapper import load_model

from notifications.tests.factories.notifications import NotificationFullFactory
from notifications.tests.factories.users import RecipientFactory

Notification = load_model("notifications", "Notification")
User = get_user_model()


@pytest.mark.parametrize(
    "method,field,initial_status,expected,expect_deleted",
    (
        ("sent", "emailed", True, 4, 2),
        ("sent", "emailed", False, 0, 0),
        ("unsent", "emailed", True, 0, 0),
        ("unsent", "emailed", False, 4, 2),
        ("public", "public", True, 4, 2),
        ("private", "public", True, 0, 0),
        ("read", "unread", False, 4, 2),
        ("read", "unread", True, 0, 0),
        ("unread", "unread", False, 0, 0),
        ("unread", "unread", True, 4, 2),
    ),
)
@pytest.mark.django_db
def test_filters(method, field, initial_status, expected, expect_deleted):
    NotificationFullFactory.create_batch(2, **{field: initial_status})
    NotificationFullFactory.create_batch(2, deleted=True, **{field: initial_status})
    func = getattr(Notification.objects, method)
    assert func().count() == expected

    with override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True}):
        assert func().count() == expect_deleted
        assert func(include_deleted=True).count() == expected


@pytest.mark.parametrize(
    "method",
    (
        "active",
        "deleted",
    ),
)
@pytest.mark.django_db
def test_filter_active_deleted(method):
    NotificationFullFactory.create_batch(2, deleted=False)
    NotificationFullFactory.create_batch(2, deleted=True)

    func = getattr(Notification.objects, method)
    with pytest.raises(ImproperlyConfigured):
        func()

    with override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True}):
        assert func().count() == 2


@pytest.mark.parametrize(
    "method,field,initial_status,expected,final_status",
    (
        ("mark_all_as_sent", "emailed", False, 2, True),
        ("mark_all_as_sent", "emailed", True, 0, True),
        ("mark_all_as_unsent", "emailed", True, 2, False),
        ("mark_all_as_unsent", "emailed", False, 0, False),
        ("mark_all_as_public", "public", True, 0, True),
        ("mark_all_as_public", "public", False, 2, True),
        ("mark_all_as_private", "public", False, 0, False),
        ("mark_all_as_private", "public", True, 2, False),
        ("mark_all_as_read", "unread", False, 0, False),
        ("mark_all_as_read", "unread", True, 2, False),
        ("mark_all_as_unread", "unread", False, 2, True),
        ("mark_all_as_unread", "unread", True, 0, True),
    ),
)
@pytest.mark.django_db
def test_mark_all(method, field, initial_status, expected, final_status):
    recipient = RecipientFactory()
    NotificationFullFactory.create_batch(2, **{field: initial_status})
    NotificationFullFactory.create_batch(2, recipient=recipient, **{field: initial_status})
    func = getattr(Notification.objects, method)

    assert func(recipient=recipient) == expected
    assert func() == expected

    assert Notification.objects.filter(**{field: final_status}).count() == 4


@pytest.mark.parametrize(
    "method,initial_status",
    (
        ("mark_all_as_active", True),
        ("mark_all_as_deleted", False),
    ),
)
@pytest.mark.django_db
def test_mark_all_active_deleted(method, initial_status):
    recipient = RecipientFactory()
    NotificationFullFactory.create_batch(2, recipient=recipient, deleted=initial_status)
    NotificationFullFactory.create_batch(2, deleted=initial_status)

    func = getattr(Notification.objects, method)
    with pytest.raises(ImproperlyConfigured):
        func()

    with override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True}):
        assert func(recipient=recipient) == 2
        assert func() == 2

    assert Notification.objects.filter(deleted=not initial_status).count() == 4
