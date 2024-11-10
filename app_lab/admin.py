# app_lab/admin.py

from django.contrib import admin
from .models import Paciente, Analise, Resultado, Material, Consumivel, TipoSanguineo, BancoDeSangue
from django.contrib.auth.models import User, Group

# Personalizando a exibição de Paciente no Django Admin
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_nascimento', 'genero', 'nacionalidade', 'contacto', 'residencia', 'criado_em')
    search_fields = ['nome', 'contacto', 'genero', 'nacionalidade']
    list_filter = ('genero', 'nacionalidade', 'criado_em')
    ordering = ('nome',)

# Personalizando a exibição de Analise no Django Admin
class AnaliseAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'tipo', 'descricao', 'data_solicitacao', 'data_prevista')
    search_fields = ['paciente__nome', 'tipo', 'descricao']
    list_filter = ('tipo', 'data_solicitacao', 'data_prevista')
    ordering = ('data_solicitacao',)

# Personalizando a exibição de Resultado no Django Admin
class ResultadoAdmin(admin.ModelAdmin):
    list_display = ('analise', 'valor', 'validado', 'data_validacao', 'validado_por', 'criado_em')
    search_fields = ['analise__paciente__nome', 'valor']
    list_filter = ('validado', 'data_validacao')
    ordering = ('data_validacao',)

# Personalizando a exibição de Material no Django Admin
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'validade', 'criado_em')
    search_fields = ['nome', 'descricao']
    list_filter = ('validade', 'criado_em')
    ordering = ('validade',)

# Personalizando a exibição de Consumivel no Django Admin
class ConsumivelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'validade', 'criado_em')
    search_fields = ['nome', 'descricao']
    list_filter = ('validade', 'criado_em')
    ordering = ('validade',)

# Personalizando a exibição de TipoSanguineo no Django Admin
class TipoSanguineoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descricao')
    search_fields = ['tipo']
    list_filter = ('tipo',)
    ordering = ('tipo',)

# Personalizando a exibição de BancoDeSangue no Django Admin
class BancoDeSangueAdmin(admin.ModelAdmin):
    list_display = ('tipo_sanguineo', 'quantidade_em_unidades', 'atualizado_em')
    search_fields = ['tipo_sanguineo__tipo']
    list_filter = ('quantidade_em_unidades', 'atualizado_em')
    ordering = ('atualizado_em',)

# Registrando os modelos no Django Admin
admin.site.register(Paciente, PacienteAdmin)
admin.site.register(Analise, AnaliseAdmin)
admin.site.register(Resultado, ResultadoAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Consumivel, ConsumivelAdmin)
admin.site.register(TipoSanguineo, TipoSanguineoAdmin)
admin.site.register(BancoDeSangue, BancoDeSangueAdmin)

# Removendo o modelo de Grupo do painel de administração se não for necessário
admin.site.unregister(Group)

# Registrando a permissão para visualização de usuários e grupos
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ['username', 'first_name', 'last_name', 'email']
    list_filter = ('is_staff', 'is_active')
    ordering = ('username',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
