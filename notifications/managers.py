''' Django notifications models file '''
# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import timezone

from notifications import settings as notifications_settings

if StrictVersion(get_version()) >= StrictVersion('1.8.0'):
    from django.contrib.contenttypes.fields import GenericForeignKey  # noqa
else:
    from django.contrib.contenttypes.generic import GenericForeignKey  # noqa


EXTRA_DATA = notifications_settings.get_config()['USE_JSONFIELD']


def is_soft_delete():
    return notifications_settings.get_config()['SOFT_DELETE']


def assert_soft_delete():
    if not is_soft_delete():
        msg = """
        To use 'deleted' field, please set 'SOFT_DELETE'=True in settings.
        Otherwise NotificationQuerySet.unread and NotificationQuerySet.read do
        NOT filter by 'deleted' field.
        """
        raise ImproperlyConfigured(msg)


class NotificationQuerySet(models.query.QuerySet):
    ''' Notification QuerySet '''
    def unsent(self):
        return self.filter(emailed=False)

    def sent(self):
        return self.filter(emailed=True)

    def unread(self, include_deleted=False):
        """
        Return only unread items in the current queryset.
        """
        if is_soft_delete() and not include_deleted:
            return self.filter(read_at__isnull=True, archived_at__isnull=False)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
        # In this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(read_at__isnull=True)

    def read(self, include_deleted=False):
        """
        Return only read items in the current queryset.
        """
        if is_soft_delete() and not include_deleted:
            return self.filter(read_at__isnull=False, archived_at__isnull=False)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
        # In this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(read_at__isnull=False)

    def unseen(self, include_deleted=False):
        """
        Return only unseen items in the current queryset.
        """
        if is_soft_delete() and not include_deleted:
            return self.filter(seen_at__isnull=True, archived_at__isnull=False)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
        # In this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(seen_at__isnull=True)

    def seen(self, include_deleted=False):
        """
        Return only seen items in the current queryset.
        """
        if is_soft_delete() and not include_deleted:
            return self.filter(seen_at__isnull=False, archived_at__isnull=False)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
        # In this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(seen_at__isnull=False)

    def mark_all_as_read(self, recipient=None):
        """
        Mark as read any unread messages in the current queryset.
        Optionally, filter these by recipient first.
        """
        # We want to filter out read ones, as later we will store
        # the time they were marked as read.
        qset = self.unread(True)
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(read_at=timezone.now())

    def mark_all_as_unread(self, recipient=None):
        """
        Mark as unread any read messages in the current queryset.
        Optionally, filter these by recipient first.
        """
        qset = self.read(True)

        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(read_at=None)

    def mark_all_as_seen(self, recipient=None):
        """
        Mark as read any unseen messages in the current queryset.
        Optionally, filter these by recipient first.
        """
        # We want to filter out read ones, as later we will store
        # the time they were marked as read.
        qset = self.unseen(True)
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(seen_at=timezone.now())

    def mark_all_as_unseen(self, recipient=None):
        """
        Mark as unread any seen messages in the current queryset.
        Optionally, filter these by recipient first.
        """
        qset = self.seen(True)

        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(seen_at=None)

    def deleted(self):
        """
        Return only deleted items in the current queryset.
        """
        assert_soft_delete()
        return self.filter(archived_at__isnull=False)

    def active(self):
        """
        Return only active(un-deleted) items in the current queryset.
        """
        assert_soft_delete()
        return self.filter(archived_at__isnull=True)

    def mark_all_as_deleted(self, recipient=None):
        """
        Mark current queryset as deleted.
        Optionally, filter by recipient first.
        """
        assert_soft_delete()
        qset = self.active()
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(archived_at=timezone.now())

    def mark_all_as_active(self, recipient=None):
        """
        Mark current queryset as active(un-deleted).
        Optionally, filter by recipient first.
        """
        assert_soft_delete()
        qset = self.deleted()
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(archived_at=None)

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
