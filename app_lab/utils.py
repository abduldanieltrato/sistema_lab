# coding=utf-8
from .models import (
    Paciente, Analise, Resultado, Consumivel, BancoDeSangue, Material, Group, Permission,
    TipoSanguineo, User,
    )
from django.utils import timezone
from django.db.models import Count
from .models import Analise
from datetime import timedelta


def gerar_relatorio_analises_por_periodo(inicio, fim):
    """
    Gera um relatório de análises realizadas em um período específico.
    Retorna uma lista de dicionários com informações das análises.
    """
    analises = Analise.objects.filter(data_solicitacao__range = (inicio, fim))
    relatorio = []
    
    for analise in analises:
        relatorio.append(
                {
                        "paciente": analise.paciente.nome,
                        "tipo": analise.tipo,
                        "descricao": analise.descricao,
                        "data_solicitacao": analise.data_solicitacao,
                        "data_prevista": analise.data_prevista,
                        "status": "Completa" if analise.resultados.exists() else "Pendente"
                        }
                )
    return relatorio


def relatorio_diario():
    """Gera o relatório das análises realizadas no último dia."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 1)
    return gerar_relatorio_analises_por_periodo(inicio, hoje)


def relatorio_semanal():
    """Gera o relatório das análises realizadas na última semana."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 7)
    return gerar_relatorio_analises_por_periodo(inicio, hoje)


def relatorio_mensal():
    """Gera o relatório das análises realizadas no último mês."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 30)  # Aproximadamente 1 mês
    return gerar_relatorio_analises_por_periodo(inicio, hoje)


def relatorio_anual():
    """Gera o relatório das análises realizadas no último ano."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 365)
    return gerar_relatorio_analises_por_periodo(inicio, hoje)


def gerar_estatisticas_analises():
    """Gera estatísticas agregadas sobre as análises realizadas."""
    total_analises = Analise.objects.count()
    completas = Analise.objects.filter(resultados__isnull = False).count()
    pendentes = total_analises - completas
    
    return {
            "total": total_analises,
            "completas": completas,
            "pendentes": pendentes
            }


def gerar_relatorio_pacientes_por_periodo(inicio, fim):
    """
    Gera um relatório dos pacientes registrados ou atualizados em um período específico.
    Inclui também um resumo das análises realizadas para cada paciente.
    """
    pacientes = Paciente.objects.filter(criado_em__range = (inicio, fim))
    relatorio = []
    
    for paciente in pacientes:
        analises = Analise.objects.filter(paciente = paciente)
        relatorio.append(
                {
                        "nome": paciente.nome,
                        "data_nascimento": paciente.data_nascimento,
                        "residencia": paciente.residencia,
                        "nacionalidade": paciente.nacionalidade,
                        "genero": paciente.genero,
                        "contacto": paciente.contacto,
                        "data_cadastro": paciente.criado_em,
                        "analises": [{
                                "tipo": analise.tipo,
                                "descricao": analise.descricao,
                                "data_solicitacao": analise.data_solicitacao,
                                "status": "Completa" if analise.resultados.exists() else "Pendente"
                                } for analise in analises]
                        }
                )
    return relatorio


def relatorio_pacientes_diario():
    """Gera o relatório dos pacientes registrados no último dia."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 1)
    return gerar_relatorio_pacientes_por_periodo(inicio, hoje)


def relatorio_pacientes_semanal():
    """Gera o relatório dos pacientes registrados na última semana."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 7)
    return gerar_relatorio_pacientes_por_periodo(inicio, hoje)


def relatorio_pacientes_mensal():
    """Gera o relatório dos pacientes registrados no último mês."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 30)
    return gerar_relatorio_pacientes_por_periodo(inicio, hoje)


def relatorio_pacientes_anual():
    """Gera o relatório dos pacientes registrados no último ano."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 365)
    return gerar_relatorio_pacientes_por_periodo(inicio, hoje)


def gerar_relatorio_consumiveis_por_periodo(inicio, fim):
    """
    Gera um relatório dos consumíveis usados ou cadastrados em um período específico.
    """
    consumiveis = Consumivel.objects.filter(criado_em__range = (inicio, fim))
    relatorio = []
    
    for consumivel in consumiveis:
        relatorio.append(
                {
                        "nome": consumivel.nome,
                        "quantidade": consumivel.quantidade,
                        "descricao": consumivel.descricao,
                        "data_cadastro": consumivel.criado_em,
                        }
                )
    return relatorio


def relatorio_consumiveis_diario():
    """Gera o relatório de consumíveis registrados no último dia."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 1)
    return gerar_relatorio_consumiveis_por_periodo(inicio, hoje)


def relatorio_consumiveis_semanal():
    """Gera o relatório de consumíveis registrados na última semana."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 7)
    return gerar_relatorio_consumiveis_por_periodo(inicio, hoje)


def relatorio_consumiveis_mensal():
    """Gera o relatório de consumíveis registrados no último mês."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 30)
    return gerar_relatorio_consumiveis_por_periodo(inicio, hoje)


def relatorio_consumiveis_anual():
    """Gera o relatório de consumíveis registrados no último ano."""
    hoje = timezone.now()
    inicio = hoje - timedelta(days = 365)
    return gerar_relatorio_consumiveis_por_periodo(inicio, hoje)
