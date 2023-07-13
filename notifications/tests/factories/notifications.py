import factory
from django.contrib.contenttypes.models import ContentType

from notifications.models import Notification
from notifications.tests.factories.users import Actor, Recipient, Target

VERB_LIST = (
    "commented",
    "liked",
    "deleted",
)


class NotificationFactory(factory.django.DjangoModelFactory):
    recipient = factory.SubFactory(Recipient)

    actor = factory.SubFactory(Actor)
    actor_object_id = factory.SelfAttribute("actor.id")
    actor_content_type = factory.LazyAttribute(lambda obj: ContentType.objects.get_for_model(obj.actor))

    verb = factory.Iterator(VERB_LIST)
    description = factory.Faker("catch_phrase")

    target = factory.SubFactory(Target)
    target_object_id = factory.SelfAttribute("target.id")
    target_content_type = factory.LazyAttribute(lambda obj: ContentType.objects.get_for_model(obj.target))

    action_object = factory.SubFactory(Target)
    action_object_object_id = factory.SelfAttribute("action_object.id")
    action_object_content_type = factory.LazyAttribute(lambda obj: ContentType.objects.get_for_model(obj.action_object))

    class Meta:
        model = Notification
