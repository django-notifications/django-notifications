import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.urls import reverse
from swapper import load_model

from notifications.tests.factories.notifications import NotificationFullFactory
from notifications.tests.test_views.constants import (
    soft_delete_status_list,
    status_list,
    wrong_status_list,
)

Notification = load_model("notifications", "Notification")


VIEW_NAME = "notifications:mark_as"


@pytest.mark.parametrize("status", status_list + wrong_status_list + soft_delete_status_list)
@pytest.mark.django_db
def test_login_required(status, client):
    view_url = reverse(VIEW_NAME, args=(1, status))
    response = client.get(view_url, follow=True)
    assert response.status_code == 200
    assert len(response.redirect_chain) == 1
    assert response.redirect_chain[0][0] == f'{reverse("admin:login")}?next={view_url}'
    assert response.redirect_chain[0][1] == 302


@pytest.mark.parametrize("status", status_list + soft_delete_status_list)
@pytest.mark.django_db
def test_notification_not_found(status, client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse(VIEW_NAME, args=(9999, status)))
    assert response.status_code == 404


@pytest.mark.parametrize("status", wrong_status_list)
@pytest.mark.django_db
def test_wrong_methods(status, client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)
    response = client.get(reverse(VIEW_NAME, args=(1, status)))
    assert response.status_code == 404
    assert response.content.decode() == f'Status "{status}" not exists.'


@pytest.mark.parametrize(
    "status,field,initial_status,expected",
    (
        ("sent", "emailed", True, True),
        ("sent", "emailed", False, True),
        ("unsent", "emailed", True, False),
        ("unsent", "emailed", False, False),
        ("public", "public", True, True),
        ("public", "public", False, True),
        ("private", "public", True, False),
        ("private", "public", False, False),
        ("read", "unread", False, False),
        ("read", "unread", True, False),
        ("unread", "unread", False, True),
        ("unread", "unread", True, True),
    ),
)
@pytest.mark.django_db
def test_mark_as(
    status, field, initial_status, expected, client, staff_user, notifications
):  # pylint: disable=unused-argument
    client.force_login(staff_user)
    notification = NotificationFullFactory(recipient=staff_user, **{field: initial_status})

    response = client.get(reverse(VIEW_NAME, args=(notification.slug, status)))
    assert response.status_code == 302
    notification.refresh_from_db()
    assert getattr(notification, field) == expected


@pytest.mark.django_db
def test_mark_as_active(client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)
    notification = NotificationFullFactory(recipient=staff_user, deleted=True)

    with pytest.raises(ImproperlyConfigured):
        response = client.get(reverse(VIEW_NAME, args=(notification.slug, "active")))

    with override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True}):
        response = client.get(reverse(VIEW_NAME, args=(notification.slug, "active")))
        assert response.status_code == 302
        notification.refresh_from_db()
        assert notification.deleted is False


@pytest.mark.django_db
def test_mark_as_deleted(client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)
    notification = NotificationFullFactory(recipient=staff_user, deleted=False)

    with override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True}):
        response = client.get(reverse(VIEW_NAME, args=(notification.slug, "deleted")))
        assert response.status_code == 302
        notification.refresh_from_db()
        assert notification.deleted is True

    response = client.get(reverse(VIEW_NAME, args=(notification.slug, "deleted")))
    with pytest.raises(Notification.DoesNotExist):
        notification.refresh_from_db()
