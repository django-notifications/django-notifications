import factory
from django.conf import settings


class RecipientFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"recipient-{n}")
    first_name = factory.SelfAttribute("username")

    class Meta:
        model = settings.AUTH_USER_MODEL


class ActorFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"actor-{n}")
    first_name = factory.SelfAttribute("username")

    class Meta:
        model = settings.AUTH_USER_MODEL


class TargetFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"target-{n}")
    first_name = factory.SelfAttribute("username")

    class Meta:
        model = settings.AUTH_USER_MODEL
