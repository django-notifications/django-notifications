from rest_framework import mixins, viewsets


class NotificationsBaseViewSet(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    A viewset that provides default `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass