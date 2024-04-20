from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.urls import NoReverseMatch
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


@pytest.mark.django_db
def test_slug():
    notification = NotificationShortFactory()
    assert notification.id == notification.slug


@pytest.mark.parametrize(
    "before,method",
    (
        (True, "mark_as_read"),
        (False, "mark_as_unread"),
    ),
)
@pytest.mark.django_db
def test_mark_as_read_unread(before, method):
    notification = NotificationShortFactory(unread=before)

    assert Notification.objects.filter(unread=before).count() == 1
    func = getattr(notification, method)
    func()
    assert Notification.objects.filter(unread=before).count() == 0
    assert Notification.objects.filter(unread=not before).count() == 1


@pytest.mark.django_db
def test_build_url():
    notification = NotificationShortFactory()

    url = notification.actor_object_url()

    assert "<a href=" in url
    assert str(notification.actor.id) in url

    with patch("notifications.models.base.reverse") as mock:
        mock.side_effect = NoReverseMatch
        url = notification.actor_object_url()
        assert notification.actor.id == url


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
