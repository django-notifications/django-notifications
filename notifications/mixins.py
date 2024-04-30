from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import resolve_url
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme


class NotificationRedirectMixin:
    request: HttpRequest

    def get_redirect_url(self, *args, **kwargs) -> str:  # pylint: disable=unused-argument
        _next = self.request.GET.get("next")

        if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
            return iri_to_uri(_next)
        return resolve_url("notifications:list", filter_by="unread")
