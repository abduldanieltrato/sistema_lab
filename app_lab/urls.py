# coding=utf-8
from django.urls import path
from . import views
from .views import (
    PacienteListCreateView,
    PacienteRetrieveUpdateView,
    AnaliseListCreateView,
    AnaliseRetrieveUpdateView
)

urlpatterns = [
    # Paciente URLs
    path('pacientes/', views.listar_pacientes, name='listar_pacientes'),
    path('pacientes/criar/', views.criar_paciente, name='criar_paciente'),
    path('pacientes/', PacienteListCreateView.as_view(), name='paciente-list-create'),
    path('pacientes/<int:pk>/', PacienteRetrieveUpdateView.as_view(), name='paciente-detail-update'),
    path('analises/', AnaliseListCreateView.as_view(), name='analise-list-create'),
    path('dashboard/', views.estoque_dashboard, name='estoque_dashboard'),
    path('analises/<int:pk>/', AnaliseRetrieveUpdateView.as_view(), name='analise-detail-update'),
    path('pacientes/editar/<int:pk>/', views.editar_paciente, name='editar_paciente'),
    path('pacientes/excluir/<int:pk>/', views.excluir_paciente, name='excluir_paciente'),
    path('pacientes/exportar/csv/', views.exportar_pacientes_csv, name='exportar_pacientes_csv'),
    path('pacientes/relatorio/', views.relatorio_pacientes, name='relatorio_pacientes'),
    path('pacientes/relatorio/pdf/', views.gerar_relatorio_pacientes, name='gerar_relatorio_pacientes'),
    path('pacientes/relatorio/excel/', views.gerar_relatorio_excel_pacientes, name='gerar_relatorio_excel_pacientes'),

    # Consumível URLs
    path('consumiveis/', views.listar_consumiveis, name='listar_consumiveis'),
    path('consumiveis/criar/', views.criar_consumivel, name='criar_consumivel'),
    path('consumiveis/editar/<int:pk>/', views.editar_consumivel, name='editar_consumivel'),
    path('consumiveis/excluir/<int:pk>/', views.excluir_consumivel, name='excluir_consumivel'),

    # Análise URLs
    path('analises/', views.listar_analises, name='listar_analises'),
    path('analises/criar/', views.criar_analise, name='criar_analise'),
    path('analises/editar/<int:pk>/', views.editar_analise, name='editar_analise'),
    path('analises/excluir/<int:pk>/', views.excluir_analise, name='excluir_analise'),

    # Resultado URLs
    path('resultados/', views.listar_resultados, name='listar_resultados'),
    path('resultados/criar/', views.criar_resultado, name='criar_resultado'),
    path('resultados/editar/<int:pk>/', views.editar_resultado, name='editar_resultado'),
    path('resultados/excluir/<int:pk>/', views.excluir_resultado, name='excluir_resultado'),

    # Material URLs
    path('materiais/', views.listar_materiais, name='listar_materiais'),
    path('materiais/criar/', views.criar_material, name='criar_material'),
    path('materiais/editar/<int:pk>/', views.editar_material, name='editar_material'),
    path('materiais/excluir/<int:pk>/', views.excluir_material, name='excluir_material'),

    # Relatório Mensal
    path('relatorios/mensal/enviar/', views.enviar_relatorio_mensal, name='enviar_relatorio_mensal'),
]