import pytest

from notifications.tests.factories.notifications import NotificationFullFactory
from notifications.tests.factories.users import RecipientFactory


@pytest.mark.django_db
@pytest.fixture
def staff_user():
    user = RecipientFactory(is_staff=True)
    yield user
    user.delete()


@pytest.mark.django_db
@pytest.fixture
def common_user():
    user = RecipientFactory(is_staff=True)
    yield user
    user.delete()


@pytest.mark.django_db
@pytest.fixture
def notifications(staff_user, common_user):  # pylint: disable=redefined-outer-name
    for deleted in (True, False):
        for emailed in (True, False):
            for public in (True, False):
                for unread in (True, False):
                    NotificationFullFactory(
                        recipient=staff_user,
                        action_object=common_user,
                        deleted=deleted,
                        emailed=emailed,
                        public=public,
                        unread=unread,
                    )
                    NotificationFullFactory(
                        recipient=common_user,
                        action_object=staff_user,
                        deleted=deleted,
                        emailed=emailed,
                        public=public,
                        unread=unread,
                    )
