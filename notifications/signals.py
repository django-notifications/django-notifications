""" Django notifications signal file """
# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import Signal
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from swapper import load_model

from notifications.models.base import NotificationLevel
from notifications.settings import notification_settings

Notification = load_model("notifications", "Notification")


def notify_handler(sender, **kwargs):
    """
    Handler function to create Notification instance upon action signal call.
    """
    # Pull the options out of kwargs
    kwargs.pop("signal", None)
    actor = sender
    recipient = kwargs.pop("recipient")
    verb = kwargs.pop("verb")
    optional_objs = [(kwargs.pop(opt, None), opt) for opt in ("target", "action_object")]
    public = bool(kwargs.pop("public", True))
    description = kwargs.pop("description", None)
    timestamp = kwargs.pop("timestamp", timezone.now())
    level = kwargs.pop("level", NotificationLevel.INFO)
    actor_for_concrete_model = kwargs.pop("actor_for_concrete_model", True)

    # Check if User or Group
    if isinstance(recipient, Group):
        recipients = recipient.user_set.all()
    elif isinstance(recipient, (models.QuerySet, list)):
        recipients = recipient
    else:
        recipients = [recipient]

    new_notifications = []

    for recipient in recipients:
        newnotify = Notification(
            recipient=recipient,
            actor_content_type=ContentType.objects.get_for_model(actor, for_concrete_model=actor_for_concrete_model),
            actor_object_id=actor.pk,
            verb=str(verb),
            public=public,
            description=description,
            timestamp=timestamp,
            level=level,
        )

        # Set optional objects
        for obj, opt in optional_objs:
            if obj is not None:
                for_concrete_model = kwargs.pop(f"{opt}_for_concrete_model", True)
                setattr(newnotify, f"{opt}_object_id", obj.pk)
                setattr(
                    newnotify,
                    f"{opt}_content_type",
                    ContentType.objects.get_for_model(obj, for_concrete_model=for_concrete_model),
                )

        if kwargs and notification_settings.USE_JSONFIELD:
            # set kwargs as model column if available
            for key in list(kwargs.keys()):
                if hasattr(newnotify, key):
                    setattr(newnotify, key, kwargs.pop(key))
            newnotify.data = kwargs

        newnotify.save()
        new_notifications.append(newnotify)

    return new_notifications


notify = Signal()
