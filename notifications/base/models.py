# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
from distutils.version import \
    StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from jsonfield.fields import JSONField
from model_utils import Choices
from notifications import settings as notifications_settings
from notifications.signals import notify
from notifications.utils import id2slug
from swapper import load_model

if StrictVersion(get_version()) >= StrictVersion('1.8.0'):
    from django.contrib.contenttypes.fields import GenericForeignKey  # noqa
else:
    from django.contrib.contenttypes.generic import GenericForeignKey  # noqa

try:
    # Django >= 1.7
    from django.urls import reverse, NoReverseMatch
except ImportError:
    # Django <= 1.6
    from django.core.urlresolvers import reverse, NoReverseMatch  # pylint: disable=no-name-in-module,import-error

EXTRA_DATA = notifications_settings.get_config()['USE_JSONFIELD']


def is_soft_delete():
    return notifications_settings.get_config()['SOFT_DELETE']


def assert_soft_delete():
    if not is_soft_delete():
        # msg = """To use 'deleted' field, please set 'SOFT_DELETE'=True in settings.
        # Otherwise NotificationQuerySet.unread and NotificationQuerySet.read do NOT filter by 'deleted' field.
        # """
        msg = 'REVERTME'
        raise ImproperlyConfigured(msg)


class NotificationQuerySet(models.query.QuerySet):
    ''' Notification QuerySet '''
    def unsent(self):
        return self.filter(emailed=False)

    def sent(self):
        return self.filter(emailed=True)

    def unread(self, include_deleted=False):
        """Return only unread items in the current queryset"""
        if is_soft_delete() and not include_deleted:
            return self.filter(unread=True, deleted=False)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
        # In this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(unread=True)

    def read(self, include_deleted=False):
        """Return only read items in the current queryset"""
        if is_soft_delete() and not include_deleted:
            return self.filter(unread=False, deleted=False)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
        # In this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(unread=False)

    def mark_all_as_read(self, recipient=None):
        """Mark as read any unread messages in the current queryset.

        Optionally, filter these by recipient first.
        """
        # We want to filter out read ones, as later we will store
        # the time they were marked as read.
        qset = self.unread(True)
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(unread=False)

    def mark_all_as_unread(self, recipient=None):
        """Mark as unread any read messages in the current queryset.

        Optionally, filter these by recipient first.
        """
        qset = self.read(True)

        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(unread=True)

    def deleted(self):
        """Return only deleted items in the current queryset"""
        assert_soft_delete()
        return self.filter(deleted=True)

    def active(self):
        """Return only active(un-deleted) items in the current queryset"""
        assert_soft_delete()
        return self.filter(deleted=False)

    def mark_all_as_deleted(self, recipient=None):
        """Mark current queryset as deleted.
        Optionally, filter by recipient first.
        """
        assert_soft_delete()
        qset = self.active()
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(deleted=True)

    def mark_all_as_active(self, recipient=None):
        """Mark current queryset as active(un-deleted).
        Optionally, filter by recipient first.
        """
        assert_soft_delete()
        qset = self.deleted()
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(deleted=False)

    def mark_as_unsent(self, recipient=None):
        qset = self.sent()
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(emailed=False)

    def mark_as_sent(self, recipient=None):
        qset = self.unsent()
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(emailed=True)


class AbstractNotification(models.Model):
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
    level = models.CharField(_('level'), choices=LEVELS, default=LEVELS.info, max_length=20)

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('recipient'),
        blank=False,
    )
    unread = models.BooleanField(_('unread'), default=True, blank=False, db_index=True)

    actor_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notify_actor',
        verbose_name=_('actor content type')
    )
    actor_object_id = models.CharField(_('actor object id'), max_length=255)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')
    actor.short_description = _('actor')

    verb = models.CharField(_('verb'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)

    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notify_target',
        verbose_name=_('target content type'),
        blank=True,
        null=True
    )
    target_object_id = models.CharField(_('target object id'), max_length=255, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')
    target.short_description = _('target')

    action_object_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notify_action_object',
        verbose_name=_('action object content type'),
        blank=True,
        null=True
    )
    action_object_object_id = models.CharField(_('action object object id'), max_length=255, blank=True, null=True)
    action_object = GenericForeignKey('action_object_content_type', 'action_object_object_id')
    action_object.short_description = _('action object')

    timestamp = models.DateTimeField(_('timestamp'), default=timezone.now, db_index=True)

    public = models.BooleanField(_('public'), default=True, db_index=True)
    deleted = models.BooleanField(_('deleted'), default=False, db_index=True)
    emailed = models.BooleanField(_('emailed'), default=False, db_index=True)

    data = JSONField(_('data'), blank=True, null=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ('-timestamp',)
        # speed up notifications count query
        indexes = [
            models.Index(fields=['recipient', 'unread']),
        ]
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def __str__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'timesince': self.timesince()
        }
        if self.target:
            if self.action_object:
                return _('%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago') % ctx
            return _('%(actor)s %(verb)s %(target)s %(timesince)s ago') % ctx
        if self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s %(timesince)s ago') % ctx
        return _('%(actor)s %(verb)s %(timesince)s ago') % ctx

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)

    @property
    def slug(self):
        return id2slug(self.id)

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()

    def actor_object_url(self):
        try:
            url = reverse("admin:{0}_{1}_change".format(self.actor_content_type.app_label,
                                                        self.actor_content_type.model),
                          args=(self.actor_object_id,))
            return format_html("<a href='{url}'>{id}</a>", url=url, id=self.actor_object_id)
        except NoReverseMatch:
            return self.actor_object_id

    def action_object_url(self):
        try:
            url = reverse("admin:{0}_{1}_change".format(self.action_object_content_type.app_label,
                                                        self.action_content_type.model),
                          args=(self.action_object_id,))
            return format_html("<a href='{url}'>{id}</a>", url=url, id=self.action_object_object_id)
        except NoReverseMatch:
            return self.action_object_object_id

    def target_object_url(self):
        try:
            url = reverse("admin:{0}_{1}_change".format(self.target_content_type.app_label,
                                                        self.target_content_type.model),
                          args=(self.target_object_id,))
            return format_html("<a href='{url}'>{id}</a>", url=url, id=self.target_object_id)
        except NoReverseMatch:
            return self.target_object_id


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
    Notification = load_model('notifications', 'Notification')
    level = kwargs.pop('level', Notification.LEVELS.info)
    actor_for_concrete_model = kwargs.pop('actor_for_concrete_model', True)

    # Check if User or Group
    if isinstance(recipient, Group):
        recipients = recipient.user_set.all()
    elif isinstance(recipient, (QuerySet, list)):
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
                for_concrete_model = kwargs.pop(f'{opt}_for_concrete_model', True)
                setattr(newnotify, '%s_object_id' % opt, obj.pk)
                setattr(newnotify, '%s_content_type' % opt,
                        ContentType.objects.get_for_model(obj, for_concrete_model=for_concrete_model))

        if kwargs and EXTRA_DATA:
            # set kwargs as model column if available
            for key in list(kwargs.keys()):
                if hasattr(newnotify, key):
                    setattr(newnotify, key, kwargs.pop(key))
            newnotify.data = kwargs

        newnotify.save()
        new_notifications.append(newnotify)

    return new_notifications


# connect the signal
notify.connect(notify_handler, dispatch_uid='notifications.models.notification')
