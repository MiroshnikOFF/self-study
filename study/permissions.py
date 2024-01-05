from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    """ Предоставляет доступ только для персонала """

    def has_permission(self, request, view):
        return request.user.is_staff


class ReadOnly(permissions.BasePermission):
    """ Запрещает доступ к методам POST, PUT, PATCH, DELETE """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsStaffOrReadOnly(permissions.BasePermission):
    """ Запрещает доступ к методам POST, PUT, PATCH, DELETE для всех кроме персонала """

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return request.method in permissions.SAFE_METHODS
