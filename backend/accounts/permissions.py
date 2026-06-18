from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsAuthorityRole(BasePermission):
    """Any of HOD / Dean / Final Authority - i.e. not a student."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            'hod', 'dean', 'final_authority'
        )
