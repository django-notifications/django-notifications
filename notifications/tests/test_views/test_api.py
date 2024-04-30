import pytest
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from swapper import load_model

from notifications.tests.factories.notifications import NotificationFullFactory
from notifications.tests.test_views.constants import (
    soft_delete_status_list,
    status_list,
    wrong_status_list,
)

Notification = load_model("notifications", "Notification")


VIEW_NAME = "notifications:api"


@pytest.mark.parametrize("status", status_list + wrong_status_list + soft_delete_status_list)
@pytest.mark.django_db
def test_login_required(status, client):
    view_url = reverse(VIEW_NAME, args=(status,))
    response = client.get(view_url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_api(client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)

    for status in status_list:
        view_url = reverse(VIEW_NAME, args=(status,))
        response = client.get(view_url)
        assert response.status_code == 200, status
        data = response.json()
        assert "count" not in data
        assert len(data["list"]) == 8, status

    # All notifications
    view_url = reverse(VIEW_NAME, args=("all",))
    response = client.get(view_url)
    assert response.status_code == 200, "All notifications"
    data = response.json()
    assert "count" not in data
    assert len(data["list"]) == 10, "All notifications"

    # Wrong status
    view_url = reverse(VIEW_NAME, args=("bla",))
    response = client.get(view_url)
    assert response.status_code == 404, "Wrong status"

    for status in soft_delete_status_list:
        view_url = reverse(VIEW_NAME, args=(status,))
        with pytest.raises(ImproperlyConfigured):
            response = client.get(view_url)


@pytest.mark.django_db
def test_api_with_should_count(client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)
    view_url = reverse(VIEW_NAME, args=("unread",))

    response = client.get(f"{view_url}?count=true")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 8
    assert len(data["list"]) == 8

    response = client.get(f"{view_url}?count=false")
    assert response.status_code == 200
    data = response.json()
    assert "count" not in data
    assert len(data["list"]) == 8


@pytest.mark.django_db
def test_api_with_limit(client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)
    view_url = reverse(VIEW_NAME, args=("unread",))

    response = client.get(f"{view_url}?count=true&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 8
    assert len(data["list"]) == 2


@pytest.mark.django_db
def test_api_with_wrong_limit(client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)
    view_url = reverse(VIEW_NAME, args=("unread",))

    response = client.get(f"{view_url}?count=true&limit=bla")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 8
    assert len(data["list"]) == 8


@pytest.mark.django_db
def test_api_mark_as_read(client, staff_user, notifications):  # pylint: disable=unused-argument
    client.force_login(staff_user)
    view_url = reverse(VIEW_NAME, args=("unread",))

    response = client.get(f"{view_url}?count=true&limit=2&mark_as_read=true")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 6
    assert len(data["list"]) == 2


@pytest.mark.django_db
def test_api_extra_data(
    client,
    staff_user,
):
    client.force_login(staff_user)
    view_url = reverse(VIEW_NAME, args=("unread",))
    NotificationFullFactory(
        recipient=staff_user,
        data={
            "url": "/learn/ask-a-pro/q/test-question-9/299/",
            "other_content": "Hello my 'world'",
            "boolean": True,
            "1": 2,
        },
    )

    response = client.get(view_url)
    assert response.status_code == 200
    data = response.json()
    assert data["list"][0]["data"]["url"] == "/learn/ask-a-pro/q/test-question-9/299/"
    assert data["list"][0]["data"]["other_content"] == "Hello my 'world'"
    assert data["list"][0]["data"]["boolean"] is True
    assert data["list"][0]["data"]["1"] == 2
