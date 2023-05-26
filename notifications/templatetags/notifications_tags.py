''' Django notifications template tags file '''
# -*- coding: utf-8 -*-
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version
from django.template import Library
from django.utils.html import format_html
from django.core.cache import cache
from notifications import settings
from notifications.settings import get_config

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse  # pylint: disable=no-name-in-module,import-error

register = Library()


def get_cached_notification_unread_count(user):

    return cache.get_or_set(
        'cache_notification_unread_count',
        user.notifications.unread().count,
        settings.get_config()['CACHE_TIMEOUT']
    )

def notifications_unread(context):
    user = user_context(context)
    if not user:
        return ''
    return get_cached_notification_unread_count(user)


if StrictVersion(get_version()) >= StrictVersion('2.0'):
    notifications_unread = register.simple_tag(takes_context=True)(notifications_unread)  # pylint: disable=invalid-name
else:
    notifications_unread = register.assignment_tag(takes_context=True)(notifications_unread)  # noqa


@register.filter
def has_notification(user):
    if user:
        return user.notifications.unread().exists()
    return False


# Requires vanilla-js framework - http://vanilla-js.com/
@register.simple_tag
def register_notify_callbacks(badge_class='live_notify_badge',  # pylint: disable=too-many-arguments,missing-docstring
                              menu_class='live_notify_list',
                              refresh_period=15,
                              callbacks='',
                              api_name='list',
                              fetch=5,
                              nonce=None,
                              mark_as_read=False
                              ):
    refresh_period = int(refresh_period) * 1000

    if api_name == 'list':
        api_url = reverse('notifications:live_unread_notification_list')
    elif api_name == 'count':
        api_url = reverse('notifications:live_unread_notification_count')
    else:
        return ""
    definitions = """
        notify_badge_class='{badge_class}';
        notify_menu_class='{menu_class}';
        notify_api_url='{api_url}';
        notify_fetch_count='{fetch_count}';
        notify_unread_url='{unread_url}';
        notify_mark_all_unread_url='{mark_all_unread_url}';
        notify_refresh_period={refresh};
        notify_mark_as_read={mark_as_read};
    """.format(
        badge_class=badge_class,
        menu_class=menu_class,
        refresh=refresh_period,
        api_url=api_url,
        unread_url=reverse('notifications:unread'),
        mark_all_unread_url=reverse('notifications:mark_all_as_read'),
        fetch_count=fetch,
        mark_as_read=str(mark_as_read).lower()
    )

    # add a nonce value to the script tag if one is provided
    nonce_str = ' nonce="{nonce}"'.format(nonce=nonce) if nonce else ""

    script = '<script type="text/javascript"{nonce}>'.format(nonce=nonce_str) + definitions
    for callback in callbacks.split(','):
        script += "register_notifier(" + callback + ");"
    script += "</script>"
    return format_html(script)


@register.simple_tag(takes_context=True)
def live_notify_badge(context, badge_class='live_notify_badge'):
    user = user_context(context)
    if not user:
        return ''

    html = "<span class='{badge_class}'>{unread}</span>".format(
        badge_class=badge_class, unread=get_cached_notification_unread_count(user)
    )
    return format_html(html)


@register.simple_tag
def live_notify_list(list_class='live_notify_list'):
    html = "<ul class='{list_class}'></ul>".format(list_class=list_class)
    return format_html(html)


def user_context(context):
    if 'user' not in context:
        return None

    request = context['request']
    user = request.user
    try:
        user_is_anonymous = user.is_anonymous()
    except TypeError:  # Django >= 1.11
        user_is_anonymous = user.is_anonymous

    if user_is_anonymous:
        return None
    return user
