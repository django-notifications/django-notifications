''' Django notifications admin file '''
# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from .models import Notification

import swapper


NotificationTemplate = swapper.load_model("notifications", "NotificationTemplate")


class NotificationAdmin(admin.ModelAdmin):
    raw_id_fields = ('recipient',)
    list_display = ('recipient', 'actor',
                    'level', 'target', 'unread', 'public')
    list_filter = ('level', 'unread', 'public', 'timestamp',)

    def get_queryset(self, request):
        qs = super(NotificationAdmin, self).get_queryset(request)
        return qs.prefetch_related('actor')


class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('verb', )


# Most of this is stolen from django-import-export :)

class NotificationActionForm(ActionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        for template in NotificationTemplate.objects.all():
            choices.append((template.slug, template.verb))
        self.fields['template'].choices = choices
    template = forms.ChoiceField(label=_('Notification template'), choices=[], required=False)


class AdminNotifyActionMixin:
    def __init__(self, *args, **kwargs):

        self.action_form = NotificationActionForm
        super().__init__(*args, **kwargs)
        self.actions += (self.notify_action,)

    def notify_action(self, admin_class, request, queryset, *args, **kwargs):
        template_slug = request.POST.get('template')
        template = NotificationTemplate.objects.get(slug=template_slug)
        for reciever in queryset:
            reciever.send_templated_notification(template)
    notify_action.short_description = _("Send notification based on template")

    @property
    def media(self):
        super_media = super().media
        return forms.Media(js=super_media._js + ['notifications/action_templates.js'], css=super_media._css)


admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationTemplate, NotificationTemplateAdmin)
