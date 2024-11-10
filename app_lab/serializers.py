# coding=utf-8
from rest_framework import serializers
from .models import Paciente


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ['id', 'nome', 'data_nascimento', 'residencia', 'nacionalidade', 'genero', 'contacto', 'criado_em']
