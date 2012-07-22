Django Notifications Documentation
===================================

`django-notifications <https://github.com/brantyoung/django-notifications>`_ is a GitHub notification alike app for Django, it was derived from `django-activity-stream <https://github.com/justquick/django-activity-stream>`_

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

Installation is easy using ``pip`` and the only requirement is a recent version of Django.

::

    $ pip install django-notifications-hq

or get it from source

::

    $ git clone https://github.com/brantyoung/django-notifications
    $ cd django-notifications
    $ python setup.py install

Then to add the Django Notifications to your project add the app ``notifications`` to your ``INSTALLED_APPS`` and urlconf.

The app should go somewhere after all the apps that are going to be generating notifications like ``django.contrib.auth``::

    INSTALLED_APPS = (
        'django.contrib.auth',
        ...
        'notifications',
        ...
    )

Add the notifications urls to your urlconf::

    urlpatterns = patterns('',
        ...
        ('^inbox/notifications/', include('notifications.urls')),
        ...
    )

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

To generate an notification anywhere in your code, simply import the notify signal and send it with your actor, verb, and target.

::

    from notifications import notify

    notify.send(request.user, verb='reached level 10')
    notify.send(request.user, verb='joined', target=group)
    notify.send(request.user, verb='created comment', action_object=comment, target=group)

API
====

``Notification.objects.mark_all_as_read(recipient)`` 
-------------------------------------------------------

Mark all unread notifications received by ``recipient``.


``Notification.objects.get().mark_as_read()``
---------------------------------------------

Mark current notification as read.


``notifications_unread`` templatetags
--------------------------------------

::

    {% notifications_unread %}

Give the number of unread notifications for a user, or nothing (an empty string) for an anonymous user.

Storing the count in a variable for further processing is advised, such as::

    {% notifications_unread as unread_count %}
    ...
    {% if unread_count %}
        You have <strong>{{ unread_count }}</strong> unread notifications.
    {% endif %}


