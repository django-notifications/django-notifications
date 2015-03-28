SECRET_KEY = 'secret_key'
SOUTH_TESTS_MIGRATE = True

TESTING = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
   }
}


MIDDLEWARE_CLASSES = ()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'notifications',
)

ROOT_URLCONF = 'notifications.urls'