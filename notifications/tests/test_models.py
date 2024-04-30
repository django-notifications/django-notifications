from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings  # noqa
from django.urls import NoReverseMatch
from django.utils.timezone import localtime
from freezegun import freeze_time
from swapper import load_model

from notifications.tests.factories.notifications import (
    NotificationFullFactory,
    NotificationShortFactory,
    NotificationWithActionObjectFactory,
    NotificationWithTargetFactory,
)

Notification = load_model("notifications", "Notification")


@pytest.mark.django_db
def test__str__():
    notification = NotificationShortFactory()

    notification_str = str(notification)
    assert str(notification.actor) in notification_str
    assert str(notification.verb) in notification_str
    assert str(notification.action_object) not in notification_str
    assert str(notification.target) not in notification_str

    notification = NotificationWithTargetFactory()
    notification_str = str(notification)
    assert str(notification.actor) in notification_str
    assert str(notification.verb) in notification_str
    assert str(notification.target) in notification_str
    assert str(notification.action_object) not in notification_str

    notification = NotificationWithActionObjectFactory()
    notification_str = str(notification)
    assert str(notification.actor) in notification_str
    assert str(notification.verb) in notification_str
    assert str(notification.action_object) in notification_str
    assert str(notification.target) not in notification_str

    notification = NotificationFullFactory()
    notification_str = str(notification)
    assert str(notification.actor) in notification_str
    assert str(notification.verb) in notification_str
    assert str(notification.target) in notification_str
    assert str(notification.action_object) in notification_str


@pytest.mark.django_db
def test_slug():
    notification = NotificationShortFactory()
    assert notification.id == notification.slug


@pytest.mark.parametrize(
    "field,initial_status,method_name,expected",
    (
        ("emailed", True, "mark_as_sent", True),
        ("emailed", False, "mark_as_sent", True),
        ("emailed", True, "mark_as_unsent", False),
        ("emailed", False, "mark_as_unsent", False),
        ("public", True, "mark_as_public", True),
        ("public", False, "mark_as_public", True),
        ("public", True, "mark_as_private", False),
        ("public", False, "mark_as_private", False),
        ("unread", True, "mark_as_read", False),
        ("unread", False, "mark_as_read", False),
        ("unread", True, "mark_as_unread", True),
        ("unread", False, "mark_as_unread", True),
    ),
)
@pytest.mark.django_db
def test_mark_as_methods(field, initial_status, method_name, expected):
    notification = NotificationShortFactory(**{field: initial_status})
    func = getattr(notification, method_name)
    func()
    assert getattr(notification, field, None) is expected


@pytest.mark.django_db
def test_mark_as_active():
    notification = NotificationShortFactory(deleted=True)
    with pytest.raises(ImproperlyConfigured):
        notification.mark_as_active()

    with override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True}):
        notification.mark_as_active()
        assert notification.deleted is False


@pytest.mark.django_db
def test_mark_as_deleted():
    notification = NotificationShortFactory(deleted=False)

    with override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True}):
        notification.mark_as_deleted()
        assert notification.deleted is True

    notification.mark_as_deleted()
    assert Notification.objects.count() == 0


@pytest.mark.parametrize(
    "method,field",
    (
        ("actor_object_url", "actor"),
        ("action_object_url", "action_object"),
        ("target_object_url", "target"),
    ),
)
@pytest.mark.django_db
def test_build_url(method, field):
    notification = NotificationFullFactory()

    url = getattr(notification, method)()

    assert "<a href=" in url
    assert str(getattr(notification, field).id) in url

    with patch("notifications.models.base.reverse") as mock:
        mock.side_effect = NoReverseMatch
        url = getattr(notification, method)()
        assert getattr(notification, field).id == url


@pytest.mark.parametrize(
    "increase,expected_result",
    (
        ({"minutes": 10}, "10\xa0minutes"),
        ({"days": 2}, "2\xa0days"),
    ),
)
@pytest.mark.django_db
def test_timesince(increase, expected_result):
    initial_date = datetime(2023, 1, 1, 0, 0, 0)
    with freeze_time(initial_date):
        notification = NotificationShortFactory()
    with freeze_time(initial_date + timedelta(**increase)):
        assert notification.timesince() == expected_result


@pytest.mark.parametrize(
    "increase,expected_result",
    (
        ({"minutes": 10}, "today"),
        ({"days": 1}, "yesterday"),
    ),
)
@pytest.mark.django_db
def test_naturalday(increase, expected_result):
    initial_date = datetime(2023, 1, 1, 0, 0, 0)
    with freeze_time(initial_date):
        notification = NotificationShortFactory()
    with freeze_time(initial_date + timedelta(**increase)):
        assert notification.naturalday() == expected_result


@pytest.mark.parametrize(
    "increase,expected_result",
    (
        ({"minutes": 10}, "10\xa0minutes ago"),
        ({"days": 1}, "1\xa0day ago"),
    ),
)
@pytest.mark.django_db
def test_naturaltime(increase, expected_result):
    initial_date = datetime(2023, 1, 1, 0, 0, 0)
    with freeze_time(initial_date):
        notification = NotificationShortFactory()
    with freeze_time(initial_date + timedelta(**increase)):
        assert notification.naturaltime() == expected_result


@pytest.mark.django_db
def test_extra_data():
    data = {"url": "/learn/ask-a-pro/q/test-question-9/299/", "other_content": "Hello my 'world'"}
    notification = NotificationFullFactory(data=data)
    assert notification.data == data


@override_settings(USE_TZ=True)
@override_settings(TIME_ZONE="Asia/Shanghai")
@pytest.mark.django_db
def test_use_timezone():
    # The delta between the two events will still be less than a second despite the different timezones
    # The call to now and the immediate call afterwards will be within a short period of time, not 8 hours as the
    # test above was originally.
    notification = NotificationFullFactory()
    delta = datetime.now(tz=timezone.utc) - localtime(notification.timestamp)
    assert delta.seconds < 60


@override_settings(USE_TZ=False)
@override_settings(TIME_ZONE="Asia/Shanghai")
@pytest.mark.django_db
def test_disable_timezone():
    notification = NotificationFullFactory()
    delta = datetime.now() - notification.timestamp
    assert delta.seconds < 60
