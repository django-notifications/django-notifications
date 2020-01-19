# -*- coding: utf-8 -*-
"""
    django-notifications
    ~~~~~
    A GitHub notification alike app for Django.
    :copyright: (c) 2015 by django-notifications team.
    :license: BSD, see LICENSE.txt for more details.
"""

# PEP 386-compliant version number: N.N[.N]+[{a|b|c|rc}N[.N]+][.postN][.devN]
__version__ = '1.4.0'

default_app_config = 'notifications.apps.Config'  # pylint: disable=invalid-name


# patch jsonfield expectations until they actually update
def _patch_jsonfield_six():
    import django
    if django.VERSION >= (3,):
        from django import utils
        import six
        utils.six = six


_patch_jsonfield_six()
del _patch_jsonfield_six
