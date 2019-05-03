''' Django notifications settings file '''
# -*- coding: utf-8 -*-
from django.conf import settings


CONFIG_DEFAULTS = {
    'PAGINATE_BY': 20,
    'USE_JSONFIELD': False,
    'SOFT_DELETE': False,
    'NUM_TO_FETCH': 10,
    'GROUP_SIMILAR': False,  # False by default
    'GROUP_SIMILAR_FIELDS': {  # The fields that will determine uniqueness of the notification
        'unread': True,
        'public': '$public',  # if starts with $, it is a variable
        'emailed': False,
        'level': '$level',
        'deleted': False
    }
}


def get_config():
    user_config = getattr(settings, 'DJANGO_NOTIFICATIONS_CONFIG', {})

    config = CONFIG_DEFAULTS.copy()
    config.update(user_config)

    return config
