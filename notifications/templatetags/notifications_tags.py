""" Django notifications template tags file """
# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.template import Library
from django.urls import reverse
from django.utils.html import format_html

from notifications.settings import notification_settings

register = Library()


def get_cached_notification_unread_count(user):
    return cache.get_or_set(
        "cache_notification_unread_count",
        user.notifications_notification_related.unread().count,
        notification_settings.CACHE_TIMEOUT,
    )


@register.simple_tag(takes_context=True)
def notifications_unread(context):
    user = user_context(context)
    if not user:
        return ""
    return get_cached_notification_unread_count(user)


@register.filter
def has_notification(user):
    if user:
        return user.notifications_notification_related.unread().exists()
    return False


# Requires vanilla-js framework - http://vanilla-js.com/
@register.simple_tag
def register_notify_callbacks(
    badge_class="live_notify_badge",
    menu_class="live_notify_list",
    refresh_period=15,
    callbacks="",
    api_name="list",
    fetch=5,
    nonce=None,
    mark_as_read=False,
):
    refresh_period = int(refresh_period) * 1000

    if api_name == "list":
        api_url = reverse("notifications:live_unread_notification_list")
    elif api_name == "count":
        api_url = reverse("notifications:live_unread_notification_count")
    else:
        return ""
    definitions = f"""
        notify_badge_class='{badge_class}';
        notify_menu_class='{menu_class}';
        notify_api_url='{api_url}';
        notify_fetch_count='{fetch}';
        notify_unread_url='{reverse("notifications:list", args=("unread",))}';
        notify_mark_all_unread_url='{reverse("notifications:mark_all_as_read")}';
        notify_refresh_period={refresh_period};
        notify_mark_as_read={str(mark_as_read).lower()};
    """

    # add a nonce value to the script tag if one is provided
    nonce_str = f' nonce="{nonce}"' if nonce else ""

    script = f'<script type="text/javascript"{nonce_str}>' + definitions
    for callback in callbacks.split(","):
        script += f"register_notifier({callback});"
    script += "</script>"
    return format_html(script)


@register.simple_tag(takes_context=True)
def live_notify_badge(context, badge_class="live_notify_badge"):
    user = user_context(context)
    if not user:
        return ""

    html = f"<span class='{badge_class}'>{get_cached_notification_unread_count(user)}</span>"
    return format_html(html)


@register.simple_tag
def live_notify_list(list_class="live_notify_list"):
    html = f"<ul class='{list_class}'></ul>"
    return format_html(html)


def user_context(context):
    if "user" not in context:
        return None

    request = context["request"]
    user = request.user

    if user.is_anonymous:
        return None
    return user
