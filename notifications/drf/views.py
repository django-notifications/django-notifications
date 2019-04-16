# ## API
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notification
from notifications.drf.mixins import ArchiveMixin
from notifications.drf.serializers import NotificationSerializer, EmptySerializer


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    ArchiveMixin,
):
    """
    list:
    Use this endpoint to retrieve a list of all notificiations.

    retrieve:
    Use this endpoint to get the information of a notification.
    """
    model = Notification
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Only allow the horses the logged in user has access to.
        """
        return self.filter_archived(
            self.model.objects.filter(recipient=self.request.user)
        )

    @detail_route(
        methods=['post', ],
        serializer_class=EmptySerializer
    )
    def mark_as_seen(self, request, pk=None):
        """
        Mark the notification as seen.
        """
        # fail fast
        if pk is None:
            return Response(
                "Can't find the notification. Please try again.",
                status=status.HTTP_400_BAD_REQUEST
            )

        # get object
        notification = self.get_object()
        notification.mark_as_seen()

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK
        )

    @detail_route(
        methods=['post', ],
        serializer_class=EmptySerializer
    )
    def mark_as_unseen(self, request, pk=None):
        """
        Mark the notification as unseen.
        """
        # fail fast
        if pk is None:
            return Response(
                "Can't find the notification. Please try again.",
                status=status.HTTP_400_BAD_REQUEST
            )

        # get object
        notification = self.get_object()
        notification.mark_as_unseen()

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK
        )

    @detail_route(
        methods=['post', ],
        serializer_class=EmptySerializer
    )
    def mark_as_read(self, request, pk=None):
        """
        Mark the notification as read.
        """
        # fail fast
        if pk is None:
            return Response(
                "Can't find the notification. Please try again.",
                status=status.HTTP_400_BAD_REQUEST
            )

        # get object
        notification = self.get_object()
        notification.mark_as_read()

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK
        )

    @detail_route(
        methods=['post', ],
        serializer_class=EmptySerializer
    )
    def mark_as_unread(self, request, pk=None):
        """
        Mark the notification as unread.
        """
        # fail fast
        if pk is None:
            return Response(
                "Can't find the notification. Please try again.",
                status=status.HTTP_400_BAD_REQUEST
            )

        # get object
        notification = self.get_object()
        notification.mark_as_unread()

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK
        )

    @list_route(
        methods=['post', ],
        serializer_class=EmptySerializer
    )
    def mark_all_as_read(self, request):
        """
        Mark all the notifications as read.
        """

        # mark it
        request.user.notifications.mark_all_as_read()

        return Response(
            None,
            status=status.HTTP_200_OK
        )

    @list_route(
        methods=['post', ],
        serializer_class=EmptySerializer
    )
    def mark_all_as_unread(self, request):
        """
        Mark all the notifications as unread.
        """

        # mark it
        request.user.notifications.mark_all_as_unread()

        return Response(
            None,
            status=status.HTTP_200_OK
        )

    @list_route(
        methods=['post', ],
        serializer_class=EmptySerializer
    )
    def mark_all_as_seen(self, request):
        """
        Mark all the notifications as seen.
        """

        # mark it
        request.user.notifications.mark_all_as_seen()

        return Response(
            None,
            status=status.HTTP_200_OK
        )

    @list_route(
        methods=['post', ],
        serializer_class=EmptySerializer
    )
    def mark_all_as_unseen(self, request):
        """
        Mark all the notifications as unseen.
        """

        # mark it
        request.user.notifications.mark_all_as_unseen()

        return Response(
            None,
            status=status.HTTP_200_OK
        )
