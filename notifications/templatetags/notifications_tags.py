# -*- coding: utf-8 -*-
from django.template import Library
from django.template.base import TemplateSyntaxError
from django.template import Node

register = Library()

@register.assignment_tag(takes_context=True)
def notifications_unread(context):
    if 'user' not in context:
        return ''
    
    user = context['user']
    if user.is_anonymous():
        return ''
    return user.notifications.unread().count()