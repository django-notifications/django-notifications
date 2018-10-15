''' Django notifications settings file '''
# -*- coding: utf-8 -*-
from django.conf import settings


CONFIG_DEFAULTS = {
    'PAGINATE_BY': 20,
    'USE_JSONFIELD': False,
    'SOFT_DELETE': False,
    'NUM_TO_FETCH': 10,
}


class NotificationSettings(object):

    def _get_config(self, config_name):
        _settings = getattr(settings, 'DJANGO_NOTIFICATIONS_CONFIG', {})
        return _settings.get(config_name, CONFIG_DEFAULTS[config_name])

    @property
    def USE_JSONFIELD(self):
        return self._get_config('USE_JSONFIELD')

    @property
    def PAGINATE_BY(self):
        return self._get_config('PAGINATE_BY')

    @property
    def SOFT_DELETE(self):
        return self._get_config('SOFT_DELETE')

    @property
    def NUM_TO_FETCH(self):
        return self._get_config('NUM_TO_FETCH')


notifications_settings = NotificationSettings()
