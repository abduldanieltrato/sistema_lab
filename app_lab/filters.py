# coding=utf-8
import django_filters
from django_filters import rest_framework as filters
from .models import Paciente, Analise, Resultado, TipoSanguineo, BancoDeSangue, Material, Consumivel




# Paciente
class PacienteFilter(filters.FilterSet):
    nome = filters.CharFilter(lookup_expr='icontains')
    data_nascimento = filters.DateFilter()
    genero = filters.ChoiceFilter(choices=Paciente.GENERO_CHOICES)

    class Meta:
        model = Paciente
        fields = ['nome', 'data_nascimento', 'genero']


class ConsumivelFilter(filters.FilterSet):
    nome = filters.CharFilter(lookup_expr='icontains')
    quantidade = filters.NumberFilter()
    criado_em = filters.DateFromToRangeFilter()

    class Meta:
        model = Consumivel
        fields = ['nome', 'quantidade', 'criado_em']


class AnaliseFilter(filters.FilterSet):
    descricao = filters.CharFilter(lookup_expr='icontains')
    status = filters.ChoiceFilter(choices=Analise.STATUS_CHOICES)
    criado_em = filters.DateFromToRangeFilter()

    class Meta:
        model = Analise
        fields = ['descricao', 'status', 'criado_em']


from .models import Resultado

class ResultadoFilter(filters.FilterSet):
    descricao = filters.CharFilter(lookup_expr='icontains')
    status = filters.ChoiceFilter(choices=Resultado.STATUS_CHOICES)
    criado_em = filters.DateFromToRangeFilter()

    class Meta:
        model = Resultado
        fields = ['descricao', 'status', 'criado_em']


class MaterialFilter(filters.FilterSet):
    nome = filters.CharFilter(lookup_expr='icontains')
    quantidade = filters.NumberFilter()
    criado_em = filters.DateFromToRangeFilter()

    class Meta:
        model = Material
        fields = ['nome', 'quantidade', 'criado_em']


class BancoDeSangueFilter(django_filters.FilterSet):
    tipo_sanguineo = django_filters.CharFilter(lookup_expr='icontains')
    estoque_minimo = django_filters.NumberFilter(lookup_expr='gte')

    class Meta:
        model = BancoDeSangue
        fields = ['tipo_sanguineo', 'estoque_minimo']