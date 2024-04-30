import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings  # noqa
from django.urls import reverse

from .constants import soft_delete_status_list, status_list, wrong_status_list

VIEW_NAME = "notifications:list"


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
def test_filter_by_status(client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)
    for status in status_list:
        response = client.get(reverse(VIEW_NAME, args=(status,)))
        assert response.status_code == 200, status
        assert len(response.context["notifications"]) == 8, status

    for status in soft_delete_status_list:
        with pytest.raises(ImproperlyConfigured):
            response = client.get(reverse(VIEW_NAME, args=(status,)))

    for status in wrong_status_list:
        response = client.get(reverse(VIEW_NAME, args=(status,)))
        assert response.status_code == 200, status
        assert len(response.context["notifications"]) == 16, status


@override_settings(DJANGO_NOTIFICATIONS_CONFIG={"SOFT_DELETE": True})
@pytest.mark.django_db
def test_filter_by_status_with_deleted(client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)

    for status in status_list:
        response = client.get(reverse(VIEW_NAME, args=(status,)))
        assert response.status_code == 200, status
        assert len(response.context["notifications"]) == 4, status

    for status in soft_delete_status_list:
        response = client.get(reverse(VIEW_NAME, args=(status,)))
        assert response.status_code == 200, status
        assert len(response.context["notifications"]) == 8, status

    for status in wrong_status_list:
        response = client.get(reverse(VIEW_NAME, args=(status,)))
        assert response.status_code == 200, status
        assert len(response.context["notifications"]) == 16, status
