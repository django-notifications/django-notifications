from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class ArchivedFilter(admin.SimpleListFilter):
    title = _('archived')
    parameter_name = 'archived_at'

    def lookups(self, request, model_admin):
        return (
            (False, _('Archived')),
            (True, _('Not archived')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            if value == 'False':
                return queryset.filter(archived_at__isnull=False)
            else:
                return queryset.filter(archived_at__isnull=True)


class ReadFilter(admin.SimpleListFilter):
    title = _('read')
    parameter_name = 'read_at'

    def lookups(self, request, model_admin):
        return (
            (False, _('Read')),
            (True, _('Not read')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            if value == 'False':
                return queryset.filter(read_at__isnull=False)
            else:
                return queryset.filter(read_at__isnull=True)


class SeenFilter(admin.SimpleListFilter):
    title = _('seen')
    parameter_name = 'seen_at'

    def lookups(self, request, model_admin):
        return (
            (False, _('Seen')),
            (True, _('Not seen')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            if value == 'False':
                return queryset.filter(seen_at__isnull=False)
            else:
                return queryset.filter(seen_at__isnull=True)
