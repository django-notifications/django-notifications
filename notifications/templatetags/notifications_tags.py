# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.template import Library

register = Library()


@register.assignment_tag(takes_context=True)
def notifications_unread(context):
    user = user_context(context)
    if not user:
        return ''
    return user.notifications.unread().count()


# Requires vanilla-js framework - http://vanilla-js.com/
@register.simple_tag
def register_notify_callbacks(badge_id='live_notify_badge',
                              menu_id='live_notify_list',
                              refresh_period=15,
                              callbacks='',
                              api_name='list',
                              fetch=5):
    refresh_period = int(refresh_period)*1000

    if api_name == 'list':
        api_url = reverse('notifications:live_unread_notification_list')
    elif api_name == 'count':
        api_url = reverse('notifications:live_unread_notification_count')
    else:
        return ""
    definitions = """
        notify_badge_id='{badge_id}';
        notify_menu_id='{menu_id}';
        notify_api_url='{api_url}';
        notify_fetch_count='{fetch_count}';
        notify_unread_url='{unread_url}';
        notify_mark_all_unread_url='{mark_all_unread_url}';
        notify_refresh_period={refresh};
    """.format(
        badge_id=badge_id,
        menu_id=menu_id,
        refresh=refresh_period,
        api_url=api_url,
        unread_url=reverse('notifications:unread'),
        mark_all_unread_url=reverse('notifications:mark_all_as_read'),
        fetch_count=fetch
    )

    script = "<script>"+definitions
    for callback in callbacks.split(','):
        script += "register_notifier("+callback+");"
    script += "</script>"
    return script


@register.simple_tag(takes_context=True)
def live_notify_badge(context, badge_id='live_notify_badge', classes=""):
    user = user_context(context)
    if not user:
        return ''

    html = "<span id='{badge_id}' class='{classes}'>{unread}</span>".format(
        badge_id=badge_id, classes=classes, unread=user.notifications.unread().count()
    )
    return html


@register.simple_tag
def live_notify_list(list_id='live_notify_list', classes=""):
    html = "<ul id='{list_id}' class='{classes}'></ul>".format(list_id=list_id, classes=classes)
    return html


def user_context(context):
    if 'user' not in context:
        return None

    request = context['request']
    user = request.user
    if user.is_anonymous():
        return None
    return user
