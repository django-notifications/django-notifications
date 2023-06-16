from django.conf import settings
import factory


class Recipient(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"recipient-{n}")
    first_name = factory.SelfAttribute("username")

    class Meta:
        model = settings.AUTH_USER_MODEL


class Actor(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"actor-{n}")
    first_name = factory.SelfAttribute("username")

    class Meta:
        model = settings.AUTH_USER_MODEL


class Target(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"target-{n}")
    first_name = factory.SelfAttribute("username")

    class Meta:
        model = settings.AUTH_USER_MODEL
