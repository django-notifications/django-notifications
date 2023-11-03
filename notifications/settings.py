""" Django notifications settings file """
# -*- coding: utf-8 -*-
from typing import Any, TypedDict, Union

from django.conf import settings

# Import from `django.core.signals` instead of the official location
# `django.test.signals` to avoid importing the test module unnecessarily.
from django.core.signals import setting_changed

NOTIFICATION_DEFAULTS = {
    "PAGINATE_BY": 20,
    "USE_JSONFIELD": False,
    "SOFT_DELETE": False,
    "NUM_TO_FETCH": 10,
    "CACHE_TIMEOUT": 2,
}


class NotificationDefaultsType(TypedDict):
    PAGINATE_BY: int
    USE_JSONFIELD: bool
    SOFT_DELETE: bool
    NUM_TO_FETCH: int
    CACHE_TIMEOUT: int


class NotificationSettings:
    """
    A settings object that allows Notification settings to be accessed as
    properties. For example:

        from notifications.settings import notification_settings
        print(notification_settings.SOFT_DELETE)

    Note:
    This is an internal class that is only compatible with settings namespaced
    under the DJANGO_NOTIFICATIONS_CONFIG name. It is not intended to be used by 3rd-party
    apps, and test helpers like `override_settings` may not work as expected.
    """

    def __init__(self, defaults: Union[None, NotificationDefaultsType] = None):
        self._user_settings: Union[NotificationDefaultsType, None] = None
        self.defaults = defaults or NotificationDefaultsType(**NOTIFICATION_DEFAULTS)  # type: ignore[typeddict-item]
        self._cached_attrs: set[str] = set()

    @property
    def user_settings(self) -> NotificationDefaultsType:
        if not self._user_settings:
            self._user_settings = NotificationDefaultsType(
                **getattr(settings, "DJANGO_NOTIFICATIONS_CONFIG") or {}
            )  # type: ignore[typeddict-item]
        return self._user_settings

    def __getattr__(self, attr: str) -> NotificationDefaultsType:
        if attr not in self.defaults:
            raise AttributeError(f'Invalid Notification setting: "{attr}"')

        try:
            # Check if present in user settings
            val = self.user_settings[attr]  # type: ignore[literal-required]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]  # type: ignore[literal-required]

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        self._user_settings = None


notification_settings = NotificationSettings(
    NotificationDefaultsType(**NOTIFICATION_DEFAULTS)  # type: ignore[typeddict-item]
)


def reload_notification_settings(*args: Any, **kwargs: Any):  # pylint: disable=unused-argument
    setting = kwargs["setting"]
    if setting == "DJANGO_NOTIFICATIONS_CONFIG":
        notification_settings.reload()


setting_changed.connect(reload_notification_settings)

__all__ = ("notification_settings",)
