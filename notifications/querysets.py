from typing import Type, Union

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import gettext_lazy as _

from notifications.settings import notification_settings
from notifications.types import AbstractUser


def assert_soft_delete() -> None:
    if not notification_settings.SOFT_DELETE:
        # msg = """To use 'deleted' field, please set 'SOFT_DELETE'=True in settings.
        # Otherwise NotificationQuerySet.unread and NotificationQuerySet.read do NOT filter by 'deleted' field.
        # """
        msg = "REVERTME"
        raise ImproperlyConfigured(msg)


class NotificationQuerySet(models.QuerySet):
    """Notification QuerySet"""

    def unsent(self) -> "NotificationQuerySet":
        """Return only unsent items in the current queryset"""
        return self.filter(emailed=False)

    def sent(self) -> "NotificationQuerySet":
        """Return only sent items in the current queryset"""
        return self.filter(emailed=True)

    def unread(self, include_deleted: bool = False) -> "NotificationQuerySet":
        """Return only unread items in the current queryset"""
        if notification_settings.SOFT_DELETE and not include_deleted:
            return self.filter(unread=True, deleted=False)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field
        # in this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(unread=True)

    def read(self, include_deleted: bool = False) -> "NotificationQuerySet":
        """Return only read items in the current queryset"""
        if notification_settings.SOFT_DELETE and not include_deleted:
            return self.filter(unread=False, deleted=False)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field
        # in this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(unread=False)

    def mark_all_as_read(self, recipient: Union[None, Type[AbstractUser]] = None) -> int:
        """Mark as read any unread messages in the current queryset.

        Optionally, filter these by recipient first.
        """
        # We want to filter out read ones, as later we will store
        # the time they were marked as read.
        qset = self.unread(True)
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(unread=False)

    def mark_all_as_unread(self, recipient: Union[None, Type[AbstractUser]] = None) -> int:
        """Mark as unread any read messages in the current queryset.

        Optionally, filter these by recipient first.
        """
        qset = self.read(True)

        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(unread=True)

    def deleted(self) -> "NotificationQuerySet":
        """Return only deleted items in the current queryset"""
        assert_soft_delete()
        return self.filter(deleted=True)

    def active(self) -> "NotificationQuerySet":
        """Return only active(un-deleted) items in the current queryset"""
        assert_soft_delete()
        return self.filter(deleted=False)

    def mark_all_as_deleted(self, recipient: Union[None, Type[AbstractUser]] = None) -> int:
        """Mark current queryset as deleted.
        Optionally, filter by recipient first.
        """
        assert_soft_delete()
        qset = self.active()
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(deleted=True)

    def mark_all_as_active(self, recipient: Union[None, Type[AbstractUser]] = None) -> int:
        """Mark current queryset as active(un-deleted).
        Optionally, filter by recipient first.
        """
        assert_soft_delete()
        qset = self.deleted()
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(deleted=False)

    def mark_as_unsent(self, recipient: Union[None, Type[AbstractUser]] = None) -> int:
        qset = self.sent()
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(emailed=False)

    def mark_as_sent(self, recipient: Union[None, Type[AbstractUser]] = None) -> int:
        qset = self.unsent()
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(emailed=True)
