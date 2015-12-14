# -*- coding: utf-8 -*-
"""
    django-notifications
    ~~~~~
    A GitHub notification alike app for Django.
    :copyright: (c) 2015 by django-notifications team.
    :license: BSD, see LICENSE.txt for more details.
"""

# PEP 386-compliant version number: N.N[.N]+[{a|b|c|rc}N[.N]+][.postN][.devN]
__version__ = '0.8.0'

try:
    from notifications.signals import notify
except ImportError:
    pass

try:
    from notifications.urls import urlpatterns
    urls = (urlpatterns, 'notifications', 'notifications')
except ImportError:
    pass
