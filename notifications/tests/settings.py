import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = 'secret_key'

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
)

# Django >= 2.0
MIDDLEWARE = MIDDLEWARE_CLASSES

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'notifications.tests',
    'notifications',
)

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
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

NOTIFICATIONS_USE_JSONFIELD = True
