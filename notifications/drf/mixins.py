# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models.fields.related import ForeignKey
from django.utils import timezone
from django.db.models.deletion import Collector
from rest_framework import mixins


class ArchiveMixin(object):
    def perform_destroy(self, instance):
        instance.archived_at = timezone.now()
        instance.save()

        # archive all models that are related to this
        collector = Collector(using='default')
        collector.collect([instance, ])

        if collector.data:
            # returns a ordereddict of model => set of values
            for key, value in collector.data.items():
                for item in value:
                    # see if model has archived property => should be (some still don't have it)
                    if getattr(item, 'archived', False) is None:
                        item.archived_at = timezone.now()
                        item.save()

    def filter_archived(self, queryset):
        if not hasattr(self, 'request'):
            return queryset

        # Get request
        request = getattr(self, 'request')

        # Return filtered queryset
        if 'archived' in request.query_params:
            archived = bool(request.query_params['archived'])
            return queryset.exclude(archived_at__isnull=archived)

        # Return filtered queryset
        if not request.query_params.get('include_archived', False):
            return queryset.exclude(archived_at__isnull=False)

        # Return unfiltered queryset
        return queryset


class ArchiveModelMixin(ArchiveMixin, mixins.DestroyModelMixin):
    pass


def get_related_FK(obj):
    related_objects = []
    for field in obj._meta.fields:
        if field.__class__ is ForeignKey:
            related_objects.append(getattr(obj, field.name))
    return related_objects
