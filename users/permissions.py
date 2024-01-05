from rest_framework.permissions import BasePermission


class IsOwnerOrStaff(BasePermission):
    """ Предоставляет доступ персоналу или владельцу """

    def has_permission(self, request, view):

        if request.user.is_staff:
            return True
        return request.user.pk == view.get_object().pk
