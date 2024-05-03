import pytest
from django.test import override_settings
from django.urls import reverse

MALICIOUS_NEXT_URLS = (
    "http://bla.com",
    "http://www.bla.com",
    "https://bla.com",
    "https://www.bla.com",
    "ftp://www.bla.com/file.exe",
)


@override_settings(ALLOWED_HOSTS=["www.notifications_notification_related.com"])
@pytest.mark.django_db
def test_next_url(client, staff_user):
    client.force_login(staff_user)
    query_parameters = "?var1=hello&var2=world"

    response = client.get(
        reverse("notifications:mark_all_as", args=("read",)),
        data={
            "next": reverse("notifications:list", args=("read",)) + query_parameters,
        },
        follow=True,
    )
    assert response.status_code == 200
    assert len(response.redirect_chain) == 1
    assert response.redirect_chain[0][0] == reverse("notifications:list", args=("read",)) + query_parameters
    assert response.redirect_chain[0][1] == 302


@override_settings(ALLOWED_HOSTS=["www.notifications_notification_related.com"])
@pytest.mark.django_db
def test_malicious_next_pages(client, staff_user):
    client.force_login(staff_user)
    query_parameters = "?var1=hello&var2=world"

    for next_url in MALICIOUS_NEXT_URLS:
        response = client.get(
            reverse("notifications:mark_all_as", args=("read",)),
            data={
                "next": next_url + query_parameters,
            },
            follow=True,
        )
        assert response.status_code == 200
        assert len(response.redirect_chain) == 1
        assert response.redirect_chain[0][0] == reverse("notifications:list", args=("unread",))
        assert response.redirect_chain[0][1] == 302
