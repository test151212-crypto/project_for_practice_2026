from rest_framework.permissions import BasePermission

class IsFreelancer(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'freelancer' and
                not request.user.is_blocked)

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'customer' and
                not request.user.is_blocked)

class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'moderator' and
                not request.user.is_blocked)

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsNotBlocked(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_blocked