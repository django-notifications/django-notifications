# Changelog

## 1.9.0

  - Added support for Django 5.0, 5.1, and 5.2
  - Added support for Python 3.12 and 3.13
  - Dropped support for Django < 4.2
  - Dropped support for Python < 3.9
  - Fixed distutils deprecation

## 1.8.3

  - Fixes missing static folder/files

## 1.8.2

  - Added the migration for verbose_name changes

## 1.8.0

  - Added support for Django 4.1
  - Dropped support for Django < 3.2 and Python < 3.7
  - Added indexes for GenericForeignKey fields in AbstractNotificationModel (see https://docs.djangoproject.com/en/4.1/ref/contrib/contenttypes/#generic-relations)
  - new setting 'CACHE_TIMEOUT' to cache certain result such as "notifications.unread().count".
  (a timeout value of 0 won’t cache anything).
  - #263 Fix vunerability in views
  - #233 Adds methods to convert to human readable type
  - Translate project all strings

## 1.7.0

  - Added support for Django 3.2 and Django 4.0
  - Fixed bug on IE11 for using `forEach` in notify.js

## 1.6.0

  - Added support to Django up to version 3.0
  - Added `AbstractNotification` model
  - Added prefetch for actor field in admin
  - Added never\_cache to some views to avoid no-update bug

## 1.5

Now all configs for the app are made inside the dictionary
*DJANGO\_NOTIFICATION\_CONFIG* in *settings.py*.

Default configs: `` `Python DJANGO_NOTIFICATIONS_CONFIG = {
'PAGINATE_BY': 20, 'USE_JSONFIELD': False, 'SOFT_DELETE': False,
'NUM_TO_FETCH': 10, } ``\`

  - Improve code quality. (@AlvaroLQueiroz)
  - Improve url patterns and remove duplicated code. (@julianogouveia)
  - Added a view for show all notifications. \#205 (@AlvaroLQueiroz)
  - Added a new tag to verify if an user has unread notifications. \#164
    (@AlvaroLQueiroz)
  - Improve documentation. (@pandabearcoder)
  - Fix pagination in list views. \#69 (@AlvaroLQueiroz)
  - Improve test matrix. (@AlvaroLQueiroz)

## 1.4

  - Adds support for django 2.0.0 (@jphamcsp and @nemesisdesign).
  - Adds database index for some fields (@nemesisdesign).
  - Changes the ID-based selection to a class-based selection in the
    methods
    \_\_[live\_notify\_badge](THIS%20VERSION%20HAS%20BREAKING%20CHANGES__:)
    and \_\_live\_notify\_list\_\_ (@AlvaroLQueiroz).
  - Now extra data and slug are returned on
    \_\_live\_unread\_notification\_list\_\_ API (@AlvaroLQueiroz).
  - Fix documentation issues (@archatas, @yaoelvon and @AlvaroLQueiroz).

## 1.3

  - Redirect to unread view after mark as read. (@osminogin)
  - Django 1.10 compability. (@osminogin)
  - Django Admin overhead reduction by removing the need to carry all
    recipients users. (@theromis)
  - Added option to mark as read in
    \_\_live\_unread\_notification\_list\_\_ endpoint. (@osminogin)
  - Fixed parameter name error in README.rst: there is no
    \_\_api\_url\_name\_\_ parameter, the correct name is
    \_\_api\_name\_\_ (@ikkebr)
  - Added \_\_sent()\_\_, \_\_unsent()\_\_, \_\_mark\_as\_sent()\_\_ and
    \_\_mark\_as\_unsent()\_\_ methods in the queryset. (@theromis)
  - \_\_notify.send()\_\_ now returns the list of saved Notifications
    instances. (@satyanash)
  - Now \_\_recipient\_\_ can be a User queryset. (@AlvaroLQueiroz)
  - Fix XMLHttpRequest onready event handler. (@AlvaroLQueiroz)

## 1.2

  - Django 1.9 template tag compatibility: due to `register.simple_tag`
    automatically espacing `unsafe_html` in Django 1.9, it is now
    recommended to use format\_html (@ikkebr)
  - Fixed parameter name error in README.rst: there is no to\_fetch
    parameter, the correct name is fetch (@ikkebr)
  - Add missing migration (@marcgibbons)
  - Minor documentation correction (@tkwon, @zhang-z)
  - Return updated count in QuerySet (@zhang-z)

## 1.1

  - Custom now() invocation got overlooked by PR \#113 (@yangyuvo)
  - Added sentinals for unauthenticated users, preventing a 500 error
    (@LegoStormtroopr)
  - Fix: Mark All As read fails if soft-deleted \#126 (@zhang-z)

## 1.0

The first major version that requires Django 1.7+.

  - Drop support for Django 1.6 and below (@zhang-z)
  - Django 1.9 compability (@illing2005)
  - Now depends on Django built-in migration facility,
    "south\_migrations" dependence was removed (@zhang-z)
  - Make django-notification compatible with django-model-utils \>= 2.4
    ( \#87, \#88, \#90 ) (@zhang-z)
  - Fix a RemovedInDjango110Warning in unittest (@zhang-z)
  - Fix pep8 & use setuptools (@areski)
  - Fix typo- in doc (@areski, @zhang-z)
  - Add app\_name in urls.py (@zhang-z)
  - Use Django's vendored copy of six (@funkybob)
  - Tidy with flake8 (@funkybob)
  - Remove custom now() function (@funkybob, @yangyubo)
  - notify.send() accepts User or Group (@Evidlo)

## 0.8.0

0.8 is the last major version supports Django 1.4\~1.6, version 0.8.0
will go into bugfix mode, no new features will be accepted.

  - Bugfixes for live-updater, and added a live tester page
    (@LegoStormtroopr)
  - Class-based classes (@alazaro)
  - Fixed urls in tests (@alazaro)
  - Added app\_label to Notification model in order to fix a Django 1.9
    deprecation warning (@Heldroe)
  - django-model-utils compatible issue (must \>=2.0.3 and \<2.4)
    (@zhang-z)
  - Reliable setup.py versioning (@yangyubo)

## 0.7.1

  - Able to pass level when adding notification (@Arthur)
  - Fix deprecation notice in Django 1.8 (@ashokfernandez)
  - Fix Python 3 support for notification model (@philroche)
  - Bugfix for wrong user unread notification count (@Geeknux)
  - A simple javascript API for live-updating specific fields within a
    django template (@LegoStormtroopr)
  - Add missing migration for Notification model (@shezadkhan137)

## 0.7.0

  - Add filters and displays to Django model Admin
  - Support Django 1.8, compatible with both django-south (django \<
    1.7) and built-in schema migration (django \>= 1.7)
  - Compatible with Python 3
  - Test fixtures, and integrated with travis-ci

## 0.6.2

  - Fix README.rst reStructuredText syntax format
  - Use relative imports
  - Add contributors to AUTHORS.txt

## 0.6.1

  - Add support for custom user model
  - mark\_as\_unread
  - Require django-model-utils \>= 2.0.3
  - Use different <span class="title-ref">now</span> function according
    to the <span class="title-ref">USE\_TZ</span> setting

## 0.6.0

  - Improve documentation
  - Add unicode support at admin panel or shell

## 0.5.5

Support for arbitrary data attribute.

## 0.5.1

Fix package descriptions and doc links.

## 0.5

First version based on
[django-activity-stream](https://github.com/justquick/django-activity-stream)
v0.4.3
