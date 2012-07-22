# -*- coding: utf-8 -*-
from django.template import Library
from django.template.base import TemplateSyntaxError
from notifications.models import Notification
from django.template import Node

register = Library()

class InboxCountNode(Node):
    "For use in the notifications_unread tag"
    def __init__(self, asvar=None):
        self.asvar = asvar

    def render(self, context):
        """
        Return the count of unread messages for the user found in context,
        (may be 0) or an empty string.
        """
        try:
            user = context['user']
            if user.is_anonymous():
                count = ''
            else:
                count = Notification.objects.unread_count(user)
        except (KeyError, AttributeError):
            count = ''
        if self.asvar:
            context[self.asvar] = count
            return ''
        return count

@register.tag
def notifications_unread(parser, token):
    """
    Give the number of unread notifications for a user,
    or nothing (an empty string) for an anonymous user.

    Storing the count in a variable for further processing is advised, such as::

        {% notifications_unread as unread_count %}
        ...
        {% if unread_count %}
            You have <strong>{{ unread_count }}</strong> unread notifications.
        {% endif %}
    """
    bits = token.split_contents()
    if len(bits) > 1:
        if len(bits) != 3:
            raise TemplateSyntaxError("'{0}' tag takes no argument or exactly two arguments".format(bits[0]))
        if bits[1] != 'as':
            raise TemplateSyntaxError("First argument to '{0}' tag must be 'as'".format(bits[0]))
        return InboxCountNode(bits[2])
    else:
        return InboxCountNode()
