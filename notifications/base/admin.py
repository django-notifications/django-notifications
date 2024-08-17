from django.contrib import admin


class AbstractNotificationAdmin(admin.ModelAdmin):
    raw_id_fields = ("recipient",)
    list_display = ("recipient", "actor", "level", "target", "unread", "public")
    list_filter = (
        "level",
        "unread",
        "public",
        "timestamp",
    )

    def get_queryset(self, request):
        qs = super(AbstractNotificationAdmin, self).get_queryset(request)
        return qs.prefetch_related("actor")
