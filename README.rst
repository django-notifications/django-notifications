``django-notifications`` Documentation
=======================================

|build-status| |coveralls|

`django-notifications <https://github.com/django-notifications/django-notifications>`_ is a GitHub notification alike app for Django, it was derived from `django-activity-stream <https://github.com/justquick/django-activity-stream>`_

Notifications are actually actions events, which are categorized by four main components.

 * ``Actor``. The object that performed the activity.
 * ``Verb``. The verb phrase that identifies the action of the activity.
 * ``Action Object``. *(Optional)* The object linked to the action itself.
 * ``Target``. *(Optional)* The object to which the activity was performed.

``Actor``, ``Action Object`` and ``Target`` are ``GenericForeignKeys`` to any arbitrary Django object.
An action is a description of an action that was performed (``Verb``) at some instant in time by some ``Actor`` on some optional ``Target`` that results in an ``Action Object`` getting created/updated/deleted.

For example: `justquick <https://github.com/justquick/>`_ ``(actor)`` *closed* ``(verb)`` `issue 2 <https://github.com/justquick/django-activity-stream/issues/2>`_ ``(object)`` on `activity-stream <https://github.com/justquick/django-activity-stream/>`_ ``(target)`` 12 hours ago

Nomenclature of this specification is based on the Activity Streams Spec: `<http://activitystrea.ms/specs/atom/1.0/>`_

Installation
============

Installation is easy using ``pip`` and will install all required libraries.

::

    $ pip install django-notifications-hq

or get it from source

::

    $ git clone https://github.com/django-notifications/django-notifications
    $ cd django-notifications
    $ python setup.py install

Note that `django-model-utils <http://pypi.python.org/pypi/django-model-utils>`_ will be installed: this is required for the pass-through QuerySet manager.

Then to add the Django Notifications to your project add the app ``notifications`` to your ``INSTALLED_APPS`` and urlconf.

The app should go somewhere after all the apps that are going to be generating notifications like ``django.contrib.auth``::

    INSTALLED_APPS = (
        'django.contrib.auth',
        ...
        'notifications',
        ...
    )

Add the notifications urls to your urlconf::

    import notifications

    urlpatterns = patterns('',
        ...
        url('^inbox/notifications/', include(notifications.urls)),
        ...
    )

The method of installing these urls, importing rather than using ``'notifications.urls'``, is required to ensure that the urls are installed in the ``notifications`` namespace.


How to migrate schema
=========================================

For Django 1.4~1.6
------------------

`django-south` support is shipped with `django-notifications`.

#. Install latest version (>=1.0) `django-south <http://pypi.python.org/pypi/South/>`_
#. Execute ``manage.py migrate notifications`` to migrate `django-notifications` schema

For Django 1.7
--------------

Django 1.7 has built-in support for migrations. No need to install `django-south`.

#. Execute ``manage.py migrate notifications``

Generating Notifications
=========================

Generating notifications is probably best done in a separate signal.

::

    from django.db.models.signals import post_save
    from notifications import notify
    from myapp.models import MyModel

    def my_handler(sender, instance, created, **kwargs):
        notify.send(instance, verb='was saved')

    post_save.connect(my_handler, sender=MyModel)

To generate an notification anywhere in your code, simply import the notify signal and send it with your actor, recipient, verb, and target.

::

    from notifications import notify

    notify.send(user, recipient=user, verb='you reached level 10')

    notify.send(comment.user, recipient=user, verb=u'replied', action_object=comment,
                description=comment.comment, target=comment.content_object)

    notify.send(follow_instance.user, recipient=follow_instance.follow_object, verb=u'has followed you',
                action_object=instance, description=u'', target=follow_instance.follow_object)

Extra data
----------

You can attach arbitrary data to your notifications by doing the following:

  * Add to your settings.py: ``NOTIFICATIONS_USE_JSONFIELD=True``

Then, any extra arguments you pass to ``notify.send(...)`` will be attached to the ``.data`` attribute of the notification object.
These will be serialised using the JSONField's serialiser, so you may need to take that into account: using only objects that will be serialised is a good idea.

Soft delete
-----------

By default, ``delete/(?P<slug>\d+)/`` deletes specified notification record from DB.
You can change this behaviour to "mark ``Notification.deleted`` field as ``True``" by:

  * Add to your settings.py: ``NOTIFICATIONS_SOFT_DELETE=True``

With this option, QuerySet methods ``unread`` and ``read`` contain one more filter: ``deleted=False``.
Meanwhile, QuerySet methods ``deleted``, ``active``, ``mark_all_as_deleted``, ``mark_all_as_active`` are turned on.
See more details in QuerySet methods section.

API
====

QuerySet methods
-----------------

Using ``django-model-utils``, we get the ability to add queryset methods to not only the manager, but to all querysets that will be used, including related objects. This enables us to do things like::

  Notification.objects.unread()

which returns all unread notifications. To do this for a single user, we can do::

  user = User.objects.get(pk=pk)
  user.notifications.unread()

There are some other QuerySet methods, too.

``qs.unread()``
~~~~~~~~~~~~~~~

Return all of the unread notifications, filtering the current queryset.
When ``NOTIFICATIONS_SOFT_DELETE=True``, this filter contains ``deleted=False``.

``qs.read()``
~~~~~~~~~~~~~~~

Return all of the read notifications, filtering the current queryset.
When ``NOTIFICATIONS_SOFT_DELETE=True``, this filter contains ``deleted=False``.


``qs.mark_all_as_read()`` | ``qs.mark_all_as_read(recipient)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mark all of the unread notifications in the queryset (optionally also filtered by ``recipient``) as read.


``qs.mark_all_as_unread()`` | ``qs.mark_all_as_unread(recipient)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mark all of the read notifications in the queryset (optionally also filtered by ``recipient``) as unread.

``qs.deleted()``
~~~~~~~~~~~~~~~~

Return all notifications that have ``deleted=True``, filtering the current queryset.
Must be used with ``NOTIFICATIONS_SOFT_DELETE=True``.

``qs.active()``
~~~~~~~~~~~~~~~

Return all notifications that have ``deleted=False``, filtering the current queryset.
Must be used with ``NOTIFICATIONS_SOFT_DELETE=True``.

``qs.mark_all_as_deleted()`` | ``qs.mark_all_as_deleted(recipient)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mark all notifications in the queryset (optionally also filtered by ``recipient``) as ``deleted=True``.
Must be used with ``NOTIFICATIONS_SOFT_DELETE=True``.

``qs.mark_all_as_active()`` | ``qs.mark_all_as_active(recipient)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mark all notifications in the queryset (optionally also filtered by ``recipient``) as ``deleted=False``.
Must be used with ``NOTIFICATIONS_SOFT_DELETE=True``.


Model methods
-------------

``obj.timesince([datetime])``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A wrapper for Django's ``timesince`` function.

``obj.mark_as_read()``
~~~~~~~~~~~~~~~~~~~~~~

Mark the current object as read.


Template tags
-------------

Put `{% load notifications_tags %}` in the template before you actually use notification tags.


``notifications_unread``
~~~~~~~~~~~~~~~~~~~~~~~~

::

    {% notifications_unread %}

Give the number of unread notifications for a user, or nothing (an empty string) for an anonymous user.

Storing the count in a variable for further processing is advised, such as::

    {% notifications_unread as unread_count %}
    ...
    {% if unread_count %}
        You have <strong>{{ unread_count }}</strong> unread notifications.
    {% endif %}


``django-notifications`` Team
==============================

Core contributors (in alphabetical order):

- `Samuel Spencer <https://github.com/LegoStormtroopr>`_
- `Yang Yubo <https://github.com/yangyubo>`_
- `zhang-z <https://github.com/zhang-z>`_

.. |build-status| image:: https://travis-ci.org/django-notifications/django-notifications.svg
    :target: https://travis-ci.org/django-notifications/django-notifications

.. |coveralls| image:: https://coveralls.io/repos/django-notifications/django-notifications/badge.png?branch=master
    :alt: Code coverage on coveralls
    :scale: 100%
    :target: https://coveralls.io/r/django-notifications/django-notifications?branch=master
