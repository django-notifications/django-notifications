from swapper import swappable_setting

from notifications.models.base import AbstractNotification


class Notification(AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        swappable = swappable_setting("notifications", "Notification")
