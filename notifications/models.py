from swapper import swappable_setting

from .base.models import AbstractNotification, notify_handler  # noqa


class Notification(AbstractNotification):

    class Meta(AbstractNotification.Meta):
        abstract = False
        swappable = swappable_setting('notifications', 'Notification')
