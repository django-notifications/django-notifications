''' Django notifications models file '''
# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.six import text_type
from jsonfield.fields import JSONField
from model_utils import Choices
from notifications import settings as notifications_settings
from notifications.managers import NotificationQuerySet
from notifications.signals import notify
from notifications.utils import id2slug

if StrictVersion(get_version()) >= StrictVersion('1.8.0'):
    from django.contrib.contenttypes.fields import GenericForeignKey  # noqa
else:
    from django.contrib.contenttypes.generic import GenericForeignKey  # noqa


EXTRA_DATA = notifications_settings.get_config()['USE_JSONFIELD']


class Notification(models.Model):
    """
    Action model describing the actor acting out a verb (on an optional
    target).
    Nomenclature based on http://activitystrea.ms/specs/atom/1.0/

    Generalized Format::

        <actor> <verb> <time>
        <actor> <verb> <target> <time>
        <actor> <verb> <action_object> <target> <time>

    Examples::

        <justquick> <reached level 60> <1 minute ago>
        <brosner> <commented on> <pinax/pinax> <2 hours ago>
        <washingtontimes> <started follow> <justquick> <8 minutes ago>
        <mitsuhiko> <closed> <issue 70> on <mitsuhiko/flask> <about 2 hours ago>

    Unicode Representation::

        justquick reached level 60 1 minute ago
        mitsuhiko closed issue 70 on mitsuhiko/flask 3 hours ago

    HTML Representation::

        <a href="http://oebfare.com/">brosner</a> commented on <a href="http://github.com/pinax/pinax">pinax/pinax</a> 2 hours ago # noqa

    """
    LEVELS = Choices('success', 'info', 'warning', 'error')
    level = models.CharField(
        choices=LEVELS,
        default=LEVELS.info,
        max_length=20
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        related_name='notifications',
        on_delete=models.CASCADE
    )

    actor_content_type = models.ForeignKey(
        ContentType,
        related_name='notify_actor',
        on_delete=models.CASCADE
    )
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(
        ContentType,
        related_name='notify_target',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    target_object_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    target = GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name='notify_action_object',
        on_delete=models.CASCADE
    )
    action_object_object_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    action_object = GenericForeignKey('action_object_content_type', 'action_object_object_id')

    created_at = models.DateTimeField(
        blank=True,
        null=True,
        default=timezone.now
    )
    archived_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    read_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    seen_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    # not used anymore
    unread = models.BooleanField(default=True, blank=False, db_index=True)
    timestamp = models.DateTimeField(default=timezone.now)
    public = models.BooleanField(default=True, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    emailed = models.BooleanField(default=False, db_index=True)

    data = JSONField(blank=True, null=True)
    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ('-timestamp',)
        app_label = 'notifications'

    def __unicode__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'timesince': self.timesince()
        }

        if self.target:
            if self.action_object:
                return u'%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago' % ctx

            return u'%(actor)s %(verb)s %(target)s %(timesince)s ago' % ctx

        if self.action_object:
            return u'%(actor)s %(verb)s %(action_object)s %(timesince)s ago' % ctx

        return u'%(actor)s %(verb)s %(timesince)s ago' % ctx

    def __str__(self):  # Adds support for Python 3
        return self.__unicode__()

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.created_at, now)

    @property
    def slug(self):
        return id2slug(self.id)

    def mark_as_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save()

    def mark_as_unread(self):
        if self.read_at:
            self.read_at = None
            self.save()

    def mark_as_seen(self):
        if not self.seen_at:
            self.seen_at = timezone.now()
            self.save()

    def mark_as_unseen(self):
        if self.seen_at:
            self.seen_at = None
            self.save()


def notify_handler(verb, **kwargs):
    """
    Handler function to create Notification instance upon action signal call.
    """

    # Pull the options out of kwargs
    kwargs.pop('signal', None)
    recipient = kwargs.pop('recipient')
    actor = kwargs.pop('sender')
    optional_objs = [
        (kwargs.pop(opt, None), opt)
        for opt in ('target', 'action_object')
    ]
    public = bool(kwargs.pop('public', True))
    description = kwargs.pop('description', None)
    timestamp = kwargs.pop('timestamp', timezone.now())
    level = kwargs.pop('level', Notification.LEVELS.info)

    # Check if User or Group
    if isinstance(recipient, Group):
        recipients = recipient.user_set.all()
    elif isinstance(recipient, (QuerySet, list)):
        recipients = recipient
    else:
        recipients = [recipient]

    new_notifications = []

    for recipient in recipients:
        values = {
            'recipient': recipient,
            'verb': text_type(verb),
            'public': public,
            'description': description,
            'created_at': timestamp,
            'level': level,
        }
        if actor:
            values.update({
                'actor_content_type': ContentType.objects.get_for_model(actor),
                'actor_object_id': actor.pk,
            })

        newnotify = Notification(**values)

        # Set optional objects
        for obj, opt in optional_objs:
            if obj is not None:
                setattr(newnotify, '%s_object_id' % opt, obj.pk)
                setattr(newnotify, '%s_content_type' % opt,
                        ContentType.objects.get_for_model(obj))

        if kwargs and EXTRA_DATA:
            newnotify.data = kwargs

        newnotify.save()
        new_notifications.append(newnotify)

    return new_notifications


# connect the signal
notify.connect(notify_handler, dispatch_uid='notifications.models.notification')
