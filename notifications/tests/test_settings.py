from django.conf import settings
from django.test import override_settings

from notifications.settings import NOTIFICATION_DEFAULTS, notification_settings


@override_settings(DJANGO_NOTIFICATIONS_CONFIG={})
def test_defaults():
    for setting_name, settings_value in NOTIFICATION_DEFAULTS.items():
        assert getattr(notification_settings, setting_name) == settings_value


@override_settings(DJANGO_NOTIFICATIONS_CONFIG={"USE_JSONFIELD": True})
def test_override_partial_settings():
    for setting_name, setting_value in settings.DJANGO_NOTIFICATIONS_CONFIG.items():
        assert getattr(notification_settings, setting_name) == setting_value
    assert settings.DJANGO_NOTIFICATIONS_CONFIG != NOTIFICATION_DEFAULTS
