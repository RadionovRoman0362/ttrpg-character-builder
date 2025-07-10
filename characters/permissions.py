from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Кастомное правило, которое разрешает доступ только владельцу объекта.
    """
    def has_object_permission(self, request, view, obj):
        # Права на чтение даются всем (например, для просмотра по ссылке в будущем).
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        
        # Права на запись, изменение и удаление есть только у владельца.
        return obj.player == request.user