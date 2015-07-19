# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.template import Library
from django.template.base import TemplateSyntaxError
from django.template import Node

register = Library()

@register.assignment_tag(takes_context=True)
def notifications_unread(context):
    if 'user' not in context:
        return ''

    request = context['request']
    user = request.user
    if user.is_anonymous():
        return ''
    return user.notifications.unread().count()

@register.simple_tag(takes_context=True)
def live_notify_icon(context,_id='my_live_notification_id',refresh_period=15000):
    if 'user' not in context:
        return ''

    request = context['request']
    user = request.user
    if user.is_anonymous():
        return ''
    refresh_period=int(refresh_period)
    # Requires vanilla-js framework - http://vanilla-js.com/
    definitions="""
        var refesher;
        notify_id='{_id}';
        notify_url='{url}';
        refresh_period={refresh};""".format(_id=_id,refresh=refresh_period,url=reverse('notifications:live_unread_notification_count'))
    script="<script>"+definitions+"""
        function get_unread_notifications() {
            var r = new XMLHttpRequest();
            r.open("GET", notify_url, true);
            r.onreadystatechange = function () {
                if (r.readyState != 4 || r.status != 200) { return };
                holder = document.getElementById(notify_id);
                holder.innerHTML = JSON.parse(r.responseText).count;
                setTimeout(get_unread_notifications,refresh_period);
            }
            r.send();
        }
        get_unread_notifications();
        </script>
        """
    html="<span id='{_id}' class='badge'>{unread}</span>".format(_id=_id,unread=user.notifications.unread().count())
    return script+html