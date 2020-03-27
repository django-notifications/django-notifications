import swapper

NotificationTemplate = swapper.load_model("notifications", "NotificationTemplate")


class NotificationType(AbstractClass):
    @abstractmethod
    def populate():
        pass

    @abstractmethod
    def check_condition(self, recipient):
        """
        Returns true if the notification is applicable to the recipient.
        """
        pass

    @property
    def template(self):
        template, created = NotificationTemplate.objects.get_or_create(slug=self.slug)
        if created:
            self.populate(template)
            template.save()
        return template

    def send(self, recipient):
        recipient.send_templated_notification(self.template)

    def revoke(self, recipient):
        recipient.revoke_templated_notification(self.template)

    def update(self, recipient):
        if self.check_condition(recipient):
            self.send(recipient)
        else:
            self.revoke(recipient)
