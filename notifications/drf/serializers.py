from django.contrib.auth import get_user_model

from rest_framework import serializers

from notifications.models import Notification
from notifications.drf.utils import get_related_field, get_user_serializer

User = get_user_model()
# CustomUserSerializer = get_user_serializer()
# CustomGenericNotificationRelatedField = get_related_field()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'id', 'first_name', 'last_name', 'email', 'password',
            'is_active', 'is_staff'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
        read_only_fields = ('id', 'email', 'is_staff', 'is_active')


class GenericNotificationRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return {}


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class EmptySerializer(serializers.Serializer):
    pass


class NotificationSerializer(serializers.ModelSerializer):
    recipient = get_user_serializer()(read_only=True)
    target = get_related_field()(read_only=True)
    action = get_related_field()(read_only=True)
    actor = get_related_field()(read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'level', 'recipient', 'verb', 'description',
            'created_at', 'read_at', 'seen_at', 'archived_at',
            'data', 'target', 'action', 'actor'
        )
