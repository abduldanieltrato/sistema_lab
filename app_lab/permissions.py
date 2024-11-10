# app_lab/permissions.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Paciente, Material, Consumivel
from rest_framework import permissions


def configurar_grupos():
    # Cria grupos de usuários, se não existirem
    admin_group, _ = Group.objects.get_or_create(name="Administradores")
    tecnico_group, _ = Group.objects.get_or_create(name="Tecnicos")
    gerente_group, _ = Group.objects.get_or_create(name="Gerentes")

    # Define permissões para cada grupo
    paciente_ct = ContentType.objects.get_for_model(Paciente)
    material_ct = ContentType.objects.get_for_model(Material)

    # Permissões específicas para o grupo de administradores
    admin_permissions = Permission.objects.filter(content_type__in=[paciente_ct, material_ct])
    admin_group.permissions.set(admin_permissions)

    # Permissões para técnicos (exemplo: visualizar e adicionar análises)
    tecnico_group.permissions.add(
        Permission.objects.get(codename="view_paciente"),
        Permission.objects.get(codename="add_analise"),
    )

    # Permissões para gerentes (exemplo: visualizar e editar materiais)
    gerente_group.permissions.add(
        Permission.objects.get(codename="view_material"),
        Permission.objects.get(codename="change_material"),
    )


class IsOwner(permissions.BasePermission):
    """
    Permissão personalizada para garantir que apenas o dono do objeto possa acessá-lo.
    """

    def has_object_permission(self, request, view, obj):
        # A permissão só é concedida se o usuário for o proprietário do objeto
        return obj.paciente == request.user.paciente


class CanEditAnalise(permissions.BasePermission):
    """
    Permissão personalizada para permitir que um usuário edite uma análise
    apenas se for o usuário associado ou um administrador.
    """

    def has_object_permission(self, request, view, obj):
        # Permite edição apenas para o dono da análise ou administradores
        return obj.paciente.usuario == request.user or request.user.is_staff


class CanEditResultado(permissions.BasePermission):
    """
    Permissão personalizada para permitir que um usuário edite um resultado
    apenas se for o usuário associado ou um administrador.
    """

    def has_object_permission(self, request, view, obj):
        # Permite edição apenas para o dono do resultado ou administradores
        return obj.analise.paciente.usuario == request.user or request.user.is_staff


class IsAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas administradores acessem
    ou modifiquem determinados objetos.
    """

    def has_permission(self, request, view):
        # Permite acesso apenas para administradores
        return request.user.is_staff


class CanEditMaterial(permissions.BasePermission):
    """
    Permissão personalizada para permitir que um usuário edite materiais
    apenas se for um administrador.
    """

    def has_object_permission(self, request, view, obj):
        # Permite edição apenas para administradores
        return request.user.is_staff


class CanEditConsumivel(permissions.BasePermission):
    """
    Permissão personalizada para permitir que um usuário edite consumíveis
    apenas se for um administrador.
    """

    def has_object_permission(self, request, view, obj):
        # Permite edição apenas para administradores
        return request.user.is_staff


class CanEditBancoDeSangue(permissions.BasePermission):
    """
    Permissão personalizada para permitir que um usuário edite o banco de sangue
    apenas se for um administrador.
    """

    def has_object_permission(self, request, view, obj):
        # Permite edição apenas para administradores
        return request.user.is_staff
