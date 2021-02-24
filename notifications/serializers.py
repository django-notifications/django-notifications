from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    # add target here
    class Meta:
        model = Notification
        fields = '__all__'

