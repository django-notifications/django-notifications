import swapper

NotificationTemplate = swapper.load_model("notifications", "NotificationTemplate")


class NotificationType:
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
