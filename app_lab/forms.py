# coding=utf-8

# forms.py
from django import forms
from .models import Paciente, Analise, Resultado, Material, Consumivel, TipoSanguineo, BancoDeSangue


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'


class AnaliseForm(forms.ModelForm):
    class Meta:
        model = Analise
        fields = '__all__'


class ResultadoForm(forms.ModelForm):
    class Meta:
        model = Resultado
        fields = '__all__'


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'


class ConsumivelForm(forms.ModelForm):
    class Meta:
        model = Consumivel
        fields = '__all__'


class TipoSanguineoForm(forms.ModelForm):
    class Meta:
        model = TipoSanguineo
        fields = '__all__'


class BancoDeSangueForm(forms.ModelForm):
    class Meta:
        model = BancoDeSangue
        fields = '__all__'
