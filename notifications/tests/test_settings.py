from django.conf import settings
from django.test import override_settings

from notifications.settings import NOTIFICATION_DEFAULTS, notification_settings


def test_defaults():
    for setting_name, settings_value in NOTIFICATION_DEFAULTS.items():
        assert getattr(notification_settings, setting_name) == settings_value


@override_settings(NOTIFICATION_SETTINGS={"USE_JSONFIELD": True})
def test_override_partial_settings():
    for setting_name, setting_value in settings.NOTIFICATION_SETTINGS.items():
        assert getattr(notification_settings, setting_name) == setting_value
    assert settings.NOTIFICATION_SETTINGS != NOTIFICATION_DEFAULTS
