# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.template import Library
from django.utils.html import format_html

register = Library()


@register.assignment_tag(takes_context=True)
def notifications_unread(context):
    user = user_context(context)
    if not user:
        return ''
    return user.notifications_notification_related.unread().count()


# Requires vanilla-js framework - http://vanilla-js.com/
@register.simple_tag
def register_notify_callbacks(badge_class='live_notify_badge',
                              menu_class='live_notify_list',
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
        notify_badge_class='{badge_class}';
        notify_menu_class='{menu_class}';
        notify_api_url='{api_url}';
        notify_fetch_count='{fetch_count}';
        notify_unread_url='{unread_url}';
        notify_mark_all_unread_url='{mark_all_unread_url}';
        notify_refresh_period={refresh};
    """.format(
        badge_class=badge_class,
        menu_class=menu_class,
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
    return format_html(script)


@register.simple_tag(takes_context=True)
def live_notify_badge(context, badge_class='live_notify_badge'):
    user = user_context(context)
    if not user:
        return ''

    html = "<span class='{badge_class}'>{unread}</span>".format(
        badge_class=badge_class, unread=user.notifications_notification_related.unread().count()
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
    if user.is_anonymous():
        return None
    return user
