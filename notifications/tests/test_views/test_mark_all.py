import pytest
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from swapper import load_model

from notifications.tests.test_views.constants import (
    soft_delete_status_list,
    status_list,
    wrong_status_list,
)

Notification = load_model("notifications", "Notification")

VIEW_NAME = "notifications:mark_all_as"


@pytest.mark.parametrize("status", status_list + wrong_status_list + soft_delete_status_list)
@pytest.mark.django_db
def test_login_required(status, client):
    view_url = reverse(VIEW_NAME, args=(status,))
    response = client.get(view_url, follow=True)
    assert response.status_code == 200
    assert len(response.redirect_chain) == 1
    assert response.redirect_chain[0][0] == f'{reverse("admin:login")}?next={view_url}'
    assert response.redirect_chain[0][1] == 302


@pytest.mark.django_db
def test_mark_all_as(client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)
    user_notifications = Notification.objects.filter(recipient=staff_user)
    for status in status_list:
        response = client.get(reverse(VIEW_NAME, args=(status,)))
        assert response.status_code == 302, status
        assert getattr(user_notifications, status)().count() == 16

    for status in wrong_status_list:
        response = client.get(reverse(VIEW_NAME, args=(status,)))
        assert response.status_code == 404, status

    for status in soft_delete_status_list:
        with pytest.raises(ImproperlyConfigured):
            response = client.get(reverse(VIEW_NAME, args=(status,)))
