from swapper import swappable_setting

from .base.models import AbstractNotification, AbstractNotificationTemplate, notify_handler  # noqa


class Notification(AbstractNotification):

    class Meta(AbstractNotification.Meta):
        abstract = False
        swappable = swappable_setting('notifications', 'Notification')


class NotificationTemplate(AbstractNotificationTemplate):

    class Meta(AbstractNotificationTemplate.Meta):
        abstract = False
        swappable = swappable_setting('notifications', 'NotificationTemplate')
