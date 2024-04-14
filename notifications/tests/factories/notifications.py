import factory
from django.contrib.contenttypes.models import ContentType
from swapper import load_model

from notifications.tests.factories.users import (
    ActorFactory,
    RecipientFactory,
    TargetFactory,
)

VERB_LIST_SHORT = ("reached level 60", "joined to site")

VERB_LIST_WITH_TARGET = (
    "commented on",
    "started follow",
    "liked",
)

VERB_LIST_FULL = (
    "closed",
    "opened",
    "liked",
)

Notification = load_model("notifications", "Notification")


class NotificationShortFactory(factory.django.DjangoModelFactory):
    recipient = factory.SubFactory(RecipientFactory)

    actor = factory.SubFactory(ActorFactory)
    actor_object_id = factory.SelfAttribute("actor.id")
    actor_content_type = factory.LazyAttribute(lambda obj: ContentType.objects.get_for_model(obj.actor))

    verb = factory.Iterator(VERB_LIST_SHORT)
    description = factory.Faker("catch_phrase")

    class Meta:
        model = Notification


class NotificationWithTargetFactory(NotificationShortFactory):
    verb = factory.Iterator(VERB_LIST_WITH_TARGET)

    target = factory.SubFactory(TargetFactory)
    target_object_id = factory.SelfAttribute("target.id")
    target_content_type = factory.LazyAttribute(lambda obj: ContentType.objects.get_for_model(obj.target))


class NotificationWithActionObjectFactory(NotificationShortFactory):
    verb = factory.Iterator(VERB_LIST_WITH_TARGET)
    action_object = factory.SubFactory(TargetFactory)
    action_object_object_id = factory.SelfAttribute("action_object.id")
    action_object_content_type = factory.LazyAttribute(lambda obj: ContentType.objects.get_for_model(obj.action_object))


class NotificationFullFactory(NotificationWithTargetFactory, NotificationWithActionObjectFactory):
    verb = factory.Iterator(VERB_LIST_FULL)
