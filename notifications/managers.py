from django.db import models


class NotificationManager(models.Manager):
    def unread_count(self, user):
        return self.filter(recipient=user, readed=False).count()

    def mark_all_as_read(self, recipient):
        return self.filter(recipient=recipient, readed=False).update(readed=True)
