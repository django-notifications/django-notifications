from unittest.mock import Mock, patch

import pytest
from django.core.cache import cache
from django.template import Context, Template
from django.urls import reverse_lazy
from freezegun import freeze_time
from swapper import load_model

from notifications.templatetags.notifications_tags import user_context
from notifications.tests.factories.notifications import NotificationFullFactory
from notifications.tests.factories.users import RecipientFactory

Notification = load_model("notifications", "Notification")


def render_tag(template, context):
    template = Template("{% load notifications_tags %}" + template)
    return template.render(Context(context))


@pytest.mark.django_db
def test_notifications_unread():
    assert render_tag("{% notifications_unread %}", {}) == ""

    assert (
        render_tag("{% notifications_unread %}", {"user": Mock(), "request": Mock(user=Mock(is_anonymous=True))}) == ""
    )

    notification = NotificationFullFactory()
    assert (
        render_tag(
            "{% notifications_unread %}", {"user": notification.recipient, "request": Mock(user=notification.recipient)}
        )
        == "1"
    )


@pytest.mark.django_db
def test_has_notification():
    user = RecipientFactory()
    assert render_tag("{{ user|has_notification }}", {"user": user}) == "False"

    notification = NotificationFullFactory(recipient=user)
    assert render_tag("{{ user|has_notification }}", {"user": user}) == "True"

    notification.mark_as_read()
    assert render_tag("{{ user|has_notification }}", {"user": user}) == "False"


@pytest.mark.parametrize(
    "_type,url",
    (
        ("list", reverse_lazy("notifications:live_unread_notification_list")),
        ("count", reverse_lazy("notifications:live_unread_notification_count")),
    ),
)
def test_register_notify_callbacks(_type, url):
    tag = f"{{% register_notify_callbacks badge_class='badge1' menu_class='menu2' refresh_period=10 callbacks='cb1,cb2' api_name='{_type}' fetch=50 nonce='123' mark_as_read=True %}}"  # pylint: disable=line-too-long

    render = render_tag(tag, {})

    assert "notify_badge_class='badge1'" in render
    assert "notify_menu_class='menu2'" in render
    assert "notify_refresh_period=10" in render
    assert "register_notifier(cb1);" in render
    assert "register_notifier(cb2);" in render
    assert "notify_fetch_count='50'" in render
    assert 'nonce="123"' in render
    assert "true" in render
    assert str(url) in render


@patch("notifications.templatetags.notifications_tags.user_context")
@pytest.mark.django_db
def test_live_notify_badge(user_context_mock):
    user = RecipientFactory()

    # No user
    user_context_mock.return_value = None
    assert render_tag("{% live_notify_badge %}", {}) == ""

    # User without notifications
    user_context_mock.return_value = user
    badge = render_tag("{% live_notify_badge badge_class='blafoo' %}", {})
    assert "blafoo" in badge
    assert "0" in badge

    # Cached with 0 notifications
    with freeze_time("2024-01-01 00:00:00"):
        NotificationFullFactory(recipient=user)
        badge = render_tag("{% live_notify_badge badge_class='blafoo' %}", {})
        assert "blafoo" in badge
        assert "0" in badge

    # No cache with notification
    with freeze_time("2024-01-02 00:00:00"):
        cache.clear()
        badge = render_tag("{% live_notify_badge badge_class='blafoo' %}", {})
        assert "blafoo" in badge
        assert "1" in badge


def test_live_notify_list():
    resp = render_tag("{% live_notify_list list_class='blafoo' %}", {})
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
