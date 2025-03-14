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
    Permite acesso APENAS se o usuário for dono do database associado à tabela.
    """

    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário autenticado é o dono do database relacionado à tabela
        return obj.database.user == request.user