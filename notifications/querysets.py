from django.db import models
from django.utils.translation import gettext_lazy as _

from notifications.helpers import assert_soft_delete
from notifications.notification_types import OptionalAbstractUser
from notifications.settings import notification_settings


class NotificationQuerySet(models.QuerySet):  # pylint: disable=too-many-public-methods
    """Notification QuerySet"""

    def _filter_by(self, include_deleted: bool = False, **kwargs) -> "NotificationQuerySet":
        if notification_settings.SOFT_DELETE and not include_deleted:
            return self.filter(deleted=False, **kwargs)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field
        # in this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(**kwargs)

    def active(self) -> "NotificationQuerySet":
        """If SOFT_DELETE is active, return only active items in the current queryset"""
        assert_soft_delete()
        return self.filter(deleted=False)

    def deleted(self) -> "NotificationQuerySet":
        """If SOFT_DELETE is active, return only deleted items in the current queryset"""
        assert_soft_delete()
        return self.filter(deleted=True)

    def sent(self, include_deleted: bool = False) -> "NotificationQuerySet":
        """Return only sent items in the current queryset"""
        return self._filter_by(include_deleted=include_deleted, emailed=True)

    def unsent(self, include_deleted: bool = False) -> "NotificationQuerySet":
        """Return only unsent items in the current queryset"""
        return self._filter_by(include_deleted=include_deleted, emailed=False)

    def public(self, include_deleted: bool = False) -> "NotificationQuerySet":
        """Return only public items in the current queryset"""
        return self._filter_by(include_deleted=include_deleted, public=True)

    def private(self, include_deleted: bool = False) -> "NotificationQuerySet":
        """Return only private items in the current queryset"""
        return self._filter_by(include_deleted=include_deleted, public=False)

    def read(self, include_deleted: bool = False) -> "NotificationQuerySet":
        """Return only read items in the current queryset"""
        return self._filter_by(include_deleted=include_deleted, unread=False)

    def unread(self, include_deleted: bool = False) -> "NotificationQuerySet":
        """Return only unread items in the current queryset"""
        return self._filter_by(include_deleted=include_deleted, unread=True)

    def _mark_all_as(self, recipient: OptionalAbstractUser = None, **kwargs) -> int:
        if recipient:
            return self.filter(recipient=recipient).update(**kwargs)
        return self.update(**kwargs)

    def mark_as_active(self, recipient: OptionalAbstractUser = None) -> int:
        """If SOFT_DELETE is activated, mark all deleted notifications as active."""
        assert_soft_delete()
        return self._mark_all_as(recipient=recipient, deleted=False)

    def mark_as_deleted(self, recipient: OptionalAbstractUser = None) -> int:
        """If SOFT_DELETE is activated, mark all active notifications as deleted."""
        assert_soft_delete()
        return self._mark_all_as(recipient=recipient, deleted=True)

    def mark_as_sent(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all unsent notifications as sent."""
        return self._mark_all_as(recipient=recipient, emailed=True)

    def mark_as_unsent(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all sent notifications as unsent."""
        return self._mark_all_as(recipient=recipient, emailed=False)

    def mark_as_public(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all private notifications as public."""
        return self._mark_all_as(recipient=recipient, public=True)

    def mark_as_private(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all public notifications as private."""
        return self._mark_all_as(recipient=recipient, public=False)

    def mark_as_read(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all unread notifications as read."""
        return self._mark_all_as(recipient=recipient, unread=False)

    def mark_as_unread(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all read notifications as unread."""
        return self._mark_all_as(recipient=recipient, unread=True)

    def mark_all_as_active(self, recipient: OptionalAbstractUser = None) -> int:
        """If SOFT_DELETE is activated, mark all deleted notifications as active."""
        assert_soft_delete()
        return self.deleted()._mark_all_as(recipient=recipient, deleted=False)  # pylint: disable=protected-access

    def mark_all_as_deleted(self, recipient: OptionalAbstractUser = None) -> int:
        """If SOFT_DELETE is activated, mark all active notifications as deleted."""
        assert_soft_delete()
        return self.active()._mark_all_as(recipient=recipient, deleted=True)  # pylint: disable=protected-access

    def mark_all_as_sent(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all unsent notifications as sent."""
        return self.unsent()._mark_all_as(recipient=recipient, emailed=True)  # pylint: disable=protected-access

    def mark_all_as_unsent(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all sent notifications as unsent."""
        return self.sent()._mark_all_as(recipient=recipient, emailed=False)  # pylint: disable=protected-access

    def mark_all_as_public(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all private notifications as public."""
        return self.private()._mark_all_as(recipient=recipient, public=True)  # pylint: disable=protected-access

    def mark_all_as_private(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all public notifications as private."""
        return self.public()._mark_all_as(recipient=recipient, public=False)  # pylint: disable=protected-access

    def mark_all_as_read(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all unread notifications as read."""
        return self.unread()._mark_all_as(recipient=recipient, unread=False)  # pylint: disable=protected-access

    def mark_all_as_unread(self, recipient: OptionalAbstractUser = None) -> int:
        """Mark all read notifications as unread."""
        return self.read()._mark_all_as(recipient=recipient, unread=True)  # pylint: disable=protected-access
