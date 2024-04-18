from unittest.mock import Mock, patch

import pytest
from django.urls import reverse_lazy
from freezegun import freeze_time
from swapper import load_model

from notifications.templatetags.notifications_tags import (
    has_notification,
    live_notify_badge,
    live_notify_list,
    notifications_unread,
    register_notify_callbacks,
    user_context,
)
from notifications.tests.factories.notifications import NotificationFullFactory
from notifications.tests.factories.users import RecipientFactory

Notification = load_model("notifications", "Notification")


@pytest.mark.django_db
def test_notifications_unread():
    with patch("notifications.templatetags.notifications_tags.user_context") as user_context_mock:
        user_context_mock.return_value = None
        assert notifications_unread({}) == ""

        notification = NotificationFullFactory()
        user_context_mock.return_value = notification.recipient
        assert notifications_unread({}) == 1


@pytest.mark.django_db
def test_has_notification():
    user = RecipientFactory()
    assert has_notification(user) is False

    notification = NotificationFullFactory(recipient=user)
    assert has_notification(user) is True

    notification.mark_as_read()
    assert has_notification(user) is False


@pytest.mark.parametrize(
    "_type,url",
    (
        ("list", reverse_lazy("notifications:live_unread_notification_list")),
        ("count", reverse_lazy("notifications:live_unread_notification_count")),
    ),
)
def test_register_notify_callbacks(_type, url):
    callback = register_notify_callbacks(
        badge_class="badge1",
        menu_class="menu2",
        refresh_period=10,
        callbacks="cb1,cb2",
        api_name=_type,
        fetch=50,
        nonce="123",
        mark_as_read=True,
    )

    assert "notify_badge_class='badge1'" in callback
    assert "notify_menu_class='menu2'" in callback
    assert "notify_refresh_period=10" in callback
    assert "register_notifier(cb1);" in callback
    assert "register_notifier(cb2);" in callback
    assert "notify_fetch_count='50'" in callback
    assert 'nonce="123"' in callback
    assert "true" in callback
    assert str(url) in callback


@patch("notifications.templatetags.notifications_tags.user_context")
@patch("notifications.templatetags.notifications_tags.get_cached_notification_unread_count")
@pytest.mark.django_db
def test_live_notify_badge(cache_mock, user_context_mock):
    user = RecipientFactory()

    user_context_mock.return_value = None
    assert live_notify_badge({}) == ""

    user_context_mock.return_value = user
    badge = live_notify_badge({}, badge_class="blafoo")
    assert "blafoo" in badge
    assert "0" in badge

    with freeze_time("2024-01-01 00:00:00"):
        NotificationFullFactory(recipient=user)
        badge = live_notify_badge({}, badge_class="blafoo")
        assert "blafoo" in badge
        assert "0" in badge  # Because of cache

        cache_mock.side_effect = lambda user: user.notifications.unread().count()
        badge = live_notify_badge({}, badge_class="blafoo")
        assert "blafoo" in badge
        assert "1" in badge


def test_live_notify_list():
    resp = live_notify_list("blafoo")
    assert "<ul" in resp
    assert "class='blafoo'" in resp


def test_user_context():
    assert user_context({}) is None

    with pytest.raises(KeyError):
        user_context({"user": Mock()})

    user = Mock(is_anonymous=True)
    assert user_context({"user": user, "request": Mock(user=user)}) is None

    user = Mock(is_anonymous=False)
    assert user_context({"user": user, "request": Mock(user=user)}) == user
