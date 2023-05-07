''' Django notification settings for tests '''
# -*- coding: utf-8 -*-
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = 'secret_key'  # noqa

DEBUG = True
TESTING = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite3',
    }
}

# Django < 2.0
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

# Django >= 2.0
MIDDLEWARE = MIDDLEWARE_CLASSES

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'notifications.tests',
    'notifications',
]

ROOT_URLCONF = 'notifications.tests.urls'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static-files")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'loaders' : [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGIN_REDIRECT_URL = 'test/'
LOGIN_URL = '/admin/login/'
APPEND_SLASH = True

DJANGO_NOTIFICATIONS_CONFIG = {
    'USE_JSONFIELD': True,
}
USE_TZ = True

if os.environ.get('SAMPLE_APP', False):
    INSTALLED_APPS.remove('notifications')
    INSTALLED_APPS.append('notifications.tests.sample_notifications')
    NOTIFICATIONS_NOTIFICATION_MODEL = 'sample_notifications.Notification'
    TEMPLATES[0]['DIRS'] += [os.path.join(BASE_DIR, '../templates')]
