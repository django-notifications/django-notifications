from django.urls import reverse

from notifications.tests.factories.notifications import NotificationFullFactory


def test_admin(admin_user, client):
    app_name = "notifications"
    NotificationFullFactory.create_batch(10)

    client.force_login(admin_user)

    response = client.get(reverse(f"admin:{app_name}_notification_changelist"))
    assert response.status_code == 200
