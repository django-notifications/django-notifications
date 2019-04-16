# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import random
import factory

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from factory import DjangoModelFactory
from faker import Faker

from notifications.models import Notification

fake = Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker('email')
    email = factory.Faker('email')
    is_active = True
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    recipient = factory.SubFactory(UserFactory)
    level = factory.LazyAttribute(lambda *args, **kwargs: random.choice(['success', 'info', 'warning', 'error']))
    actor_content_type = factory.Iterator(ContentType.objects.all())
    actor_object_id = factory.LazyAttribute(lambda x: random.randint(1, 10))
    target_content_type = factory.Iterator(ContentType.objects.all())
    target_object_id = factory.LazyAttribute(lambda x: random.randint(1, 10))
    action_object_content_type = factory.Iterator(ContentType.objects.all())
    action_object_object_id = factory.LazyAttribute(lambda x: random.randint(1, 10))
    verb = fake.text(max_nb_chars=100)
    description = fake.text(max_nb_chars=300)
    created_at = factory.LazyAttribute(lambda x: timezone.now())
