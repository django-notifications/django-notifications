Changelog
=========

1.5
----
__THIS VERSION HAS BREAKING CHANGES__:
Now all configs for the app are made inside the dictionary *DJANGO_NOTIFICATION_CONFIG* in *settings.py*.

Default configs:
```Python
DJANGO_NOTIFICATION_CONFIG = {
    'PAGINATE_BY': 20,
    'USE_JSONFIELD': False,
    'SOFT_DELETE': False,
    'NUM_TO_FETCH': 10,
}
```

- Improve code quality. (@AlvaroLQueiroz)
- Improve url patterns and remove duplicated code. (@julianogouveia)
- Added a view for show all notifications. #205 (@AlvaroLQueiroz)
- Added a new tag to verify if an user has unread notifications. #164 (@AlvaroLQueiroz)
- Improve documentation. (@pandabearcoder)
- Fix pagination in list views. #69 (@AlvaroLQueiroz)
- Improve test matrix. (@AlvaroLQueiroz)

1.4
----

- Adds support for django 2.0.0 (@jphamcsp and @nemesisdesign).
- Adds database index for some fields (@nemesisdesign).
- Changes the ID-based selection to a class-based selection in the methods __live_notify_badge__ and __live_notify_list__ (@AlvaroLQueiroz).
- Now extra data and slug are returned on __live_unread_notification_list__ API (@AlvaroLQueiroz).
- Fix documentation issues (@archatas, @yaoelvon and @AlvaroLQueiroz).

1.3
-----

- Redirect to unread view after mark as read. (@osminogin)
- Django 1.10 compability. (@osminogin)
- Django Admin overhead reduction by removing the need to carry all recipients users. (@theromis)
- Added option to mark as read in __live_unread_notification_list__ endpoint. (@osminogin)
- Fixed parameter name error in README.rst: there is no __api_url_name__ parameter, the correct name is __api_name__ (@ikkebr)
- Added __sent()__, __unsent()__, __mark_as_sent()__ and __mark_as_unsent()__ methods in the queryset. (@theromis)
- __notify.send()__ now returns the list of saved Notifications instances. (@satyanash)
- Now __recipient__ can be a User queryset. (@AlvaroLQueiroz)
- Fix XMLHttpRequest onready event handler. (@AlvaroLQueiroz)

1.2
-----

- Django 1.9 template tag compatibility: due to ``register.simple_tag`` automatically espacing ``unsafe_html`` in Django 1.9, it is now recommended to use format_html (@ikkebr)
- Fixed parameter name error in README.rst: there is no to_fetch parameter, the correct name is fetch (@ikkebr)
- Add missing migration (@marcgibbons)
- Minor documentation correction (@tkwon, @zhang-z)
- Return updated count in QuerySet (@zhang-z)

1.1
-----

- Custom now() invocation got overlooked by PR #113 (@yangyuvo)
- Added sentinals for unauthenticated users, preventing a 500 error (@LegoStormtroopr)
- Fix: Mark All As read fails if soft-deleted #126 (@zhang-z)

1.0
-----

The first major version that requires Django 1.7+.

- Drop support for Django 1.6 and below (@zhang-z)
- Django 1.9 compability (@illing2005)
- Now depends on Django built-in migration facility, "south_migrations" dependence was removed (@zhang-z)
- Make django-notification compatible with django-model-utils >= 2.4 ( #87, #88, #90 ) (@zhang-z)
- Fix a RemovedInDjango110Warning in unittest (@zhang-z)
- Fix pep8 & use setuptools (@areski)
- Fix typo- in doc (@areski, @zhang-z)
- Add app_name in urls.py (@zhang-z)
- Use Django's vendored copy of six (@funkybob)
- Tidy with flake8 (@funkybob)
- Remove custom now() function (@funkybob, @yangyubo)
- notify.send() accepts User or Group (@Evidlo)

0.8.0
-----

0.8 is the last major version supports Django 1.4~1.6, version 0.8.0 will go into bugfix mode, no new features will be accepted.

- Bugfixes for live-updater, and added a live tester page (@LegoStormtroopr)
- Class-based classes (@alazaro)
- Fixed urls in tests (@alazaro)
- Added app_label to Notification model in order to fix a Django 1.9 deprecation warning (@Heldroe)
- django-model-utils compatible issue (must >=2.0.3 and <2.4) (@zhang-z)
- Reliable setup.py versioning (@yangyubo)

0.7.1
-----

- Able to pass level when adding notification (@Arthur)
- Fix deprecation notice in Django 1.8 (@ashokfernandez)
- Fix Python 3 support for notification model (@philroche)
- Bugfix for wrong user unread notification count (@Geeknux)
- A simple javascript API for live-updating specific fields within a django template (@LegoStormtroopr)
- Add missing migration for Notification model (@shezadkhan137)

0.7.0
-----

- Add filters and displays to Django model Admin
- Support Django 1.8, compatible with both django-south (django < 1.7) and built-in schema migration (django >= 1.7)
- Compatible with Python 3
- Test fixtures, and integrated with travis-ci

0.6.2
-----

- Fix README.rst reStructuredText syntax format
- Use relative imports
- Add contributors to AUTHORS.txt

0.6.1
-----

- Add support for custom user model
- mark_as_unread
- Require django-model-utils >= 2.0.3
- Use different `now` function according to the `USE_TZ` setting

0.6.0
-----

- Improve documentation
- Add unicode support at admin panel or shell

0.5.5
-----

Support for arbitrary data attribute.

0.5.1
-----

Fix package descriptions and doc links.

0.5
---

First version based on `django-activity-stream <https://github.com/justquick/django-activity-stream>`_ v0.4.3
