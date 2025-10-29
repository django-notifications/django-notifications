from swapper import swappable_setting

from .base.models import AbstractNotification, notify_handler  # noqa


class Notification(AbstractNotification):

    class Meta(AbstractNotification.Meta):
        abstract = False
        swappable = swappable_setting('notifications', 'Notification')
    
    def naturalday(self):
        """
        Shortcut for the ``humanize``.
        Take a parameter humanize_type. This parameter control the which humanize method use.
        Return ``today``, ``yesterday`` ,``now``, ``2 seconds ago``etc. 
        """
        from django.contrib.humanize.templatetags.humanize import naturalday
        return naturalday(self.timestamp)

    def naturaltime(self):
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(self.timestamp)     