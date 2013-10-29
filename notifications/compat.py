# -*- coding: utf8 -*-
"""Abstraction layer to deal with Django related changes in order to keep
compatibility with several Django versions simultaneously."""
from django import VERSION as DJANGO_VERSION
from django.conf import settings as django_settings

# Django 1.5+
if DJANGO_VERSION >= (1,5):
    USER_MODEL = getattr(django_settings, 'AUTH_USER_MODEL', 'auth.User')
else:
    USER_MODEL = 'auth.User'

def get_user_model():

    if DJANGO_VERSION >= (1, 5):
        from django.contrib.auth import get_user_model as gum
        return gum()
    else:
        from django.contrib.auth.models import User
        return User
