from rest_framework import serializers
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username',]

class NotificationSerializer(serializers.ModelSerializer):
    recipient = PublicUserSerializer(read_only=True)
    unread = serializers.BooleanField(read_only=True)


    class Meta:
        model = Notification
        fields = "__all__"