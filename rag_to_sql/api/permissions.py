from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permite acesso APENAS se o usuário for dono do objeto, mesmo para leitura.
    """

    def has_object_permission(self, request, view, obj):
        # Bloqueia TODOS os métodos (GET, PUT, DELETE) se o usuário não for dono
        print("obj:", obj)
        return obj.user == request.user  # Campo correto é 'user', não 'owner'

class IsOwnerTable(permissions.BasePermission):
    """
    Permite acesso APENAS se o usuário for dono do objeto, mesmo para leitura.
    """

    def has_object_permission(self, request, view, obj):
        # Bloqueia TODOS os métodos (GET, PUT, DELETE) se o usuário não for dono
        
        return obj.user == request.user  # Campo correto é 'user', não 'owner'