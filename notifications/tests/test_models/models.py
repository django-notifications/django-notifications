from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=64)
    address = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"foo/{self.id}/"


class TargetObject(Customer):
    def get_url_for_notifications(self, notification, request):
        return f"bar/{self.id}/"
