from rest_framework import mixins, viewsets


class BaseViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    A viewset that provides default `create()`,`destroy()` and `list()`
    actions.
    """
    pass
