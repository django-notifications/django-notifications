import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import override_settings  # noqa
from django.utils.timezone import now
from swapper import load_model

from notifications.models.base import NotificationLevel
from notifications.signals import notify
from notifications.tests.factories.users import (
    ActorFactory,
    RecipientFactory,
    TargetFactory,
)

Notification = load_model("notifications", "Notification")
User = get_user_model()


@pytest.mark.django_db
def test_send():
    actor = ActorFactory()
    recipient = RecipientFactory()
    target = TargetFactory()
    action_object = TargetFactory()
    timestamp = now()
    notify.send(
        sender=actor,
        recipient=recipient,
        verb="poked",
        public=False,
        description="Testing",
        timestamp=timestamp,
        level=NotificationLevel.ERROR,
        target=target,
        action_object=action_object,
    )

    assert Notification.objects.count() == 1
    notification = Notification.objects.first()
    assert notification.actor == actor
    assert notification.recipient == recipient
    assert notification.verb == "poked"
    assert notification.public is False
    assert notification.description == "Testing"
    assert notification.timestamp == timestamp
    assert notification.level == NotificationLevel.ERROR
    assert notification.target == target
    assert notification.action_object == action_object


@pytest.mark.django_db
def test_send_to_multiple_recipients():
    actor = ActorFactory()
    group = Group.objects.create(name="group1")
    recipient1 = RecipientFactory()
    recipient2 = RecipientFactory()
    recipient1.groups.add(group)

    notify.send(sender=actor, recipient=[recipient1, recipient2], verb="poked you")
    assert Notification.objects.filter(actor_object_id=actor.id, recipient=recipient1, verb="poked you").count() == 1
    assert Notification.objects.filter(actor_object_id=actor.id, recipient=recipient2, verb="poked you").count() == 1

    recipients = User.objects.filter(username__startswith="recipient")
    notify.send(sender=actor, recipient=recipients, verb="poked you")
    assert Notification.objects.filter(actor_object_id=actor.id, recipient=recipient1, verb="poked you").count() == 2
    assert Notification.objects.filter(actor_object_id=actor.id, recipient=recipient2, verb="poked you").count() == 2

    notify.send(sender=actor, recipient=group, verb="poked you")
    assert Notification.objects.filter(actor_object_id=actor.id, recipient=recipient1, verb="poked you").count() == 3
    assert Notification.objects.filter(actor_object_id=actor.id, recipient=recipient2, verb="poked you").count() == 2


@override_settings(DJANGO_NOTIFICATIONS_CONFIG={"USE_JSONFIELD": True})
@pytest.mark.django_db
def test_extra_data():
    actor = ActorFactory()
    recipient = RecipientFactory()
    target = TargetFactory()
    action_object = TargetFactory()
    timestamp = now()
    notify.send(
        sender=actor,
        recipient=recipient,
        verb="poked",
        public=False,
        description="Testing",
        timestamp=timestamp,
        level=NotificationLevel.ERROR,
        target=target,
        action_object=action_object,
        extra1=True,
        extra2="Hello",
        extra3=3.1415,
        extra4=[1, 2],
        extra5={1: 2, "bla": True},
    )

    assert Notification.objects.count() == 1
    notification = Notification.objects.first()
    assert notification.data["extra1"] is True
    assert notification.data["extra2"] == "Hello"
    assert notification.data["extra3"] == 3.1415
    assert notification.data["extra4"] == [1, 2]
    assert notification.data["extra5"]["1"] == 2
    assert notification.data["extra5"]["bla"] is True


@override_settings(DJANGO_NOTIFICATIONS_CONFIG={"USE_JSONFIELD": False})
@pytest.mark.django_db
def test_extra_data_disabled():
    actor = ActorFactory()
    recipient = RecipientFactory()
    notify.send(
        sender=actor,
        recipient=recipient,
        verb="poked",
        extra1=True,
        extra2="Hello",
        extra3=3.1415,
        extra4=[1, 2],
        extra5={1: 2, "bla": True},
    )

    assert Notification.objects.count() == 1
    notification = Notification.objects.first()
    assert notification.data is None
