from django.db.models.signals import post_migrate
from django.contrib.auth.models import Permission
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone

# Modelos principais para o sistema de laboratório

class Paciente(models.Model):
    GENERO_CHOICES = [
        ('feminino', 'Feminino'),
        ('masculino', 'Masculino'),
        ('outro', 'Outro')
    ]
    PAIS_CHOICES = [
        ('mozambique', 'Mozambique'),
        ('estrangeiro', 'Estrangeiro')
    ]
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    residencia = models.CharField(max_length=255)
    nacionalidade = models.CharField(max_length=25, choices=PAIS_CHOICES)
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES)
    contacto = models.CharField(max_length=9)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        permissions = [
            ("can_view_sensitive_data", "Can view sensitive data"),
            ("can_export_data", "Can export data"),
        ]

class Analise(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='analises')
    tipo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_prevista = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} - {self.paciente.nome}"

class Resultado(models.Model):
    analise = models.ForeignKey(Analise, on_delete=models.CASCADE, related_name='resultados')
    valor = models.TextField()
    validado = models.BooleanField(default=False)
    data_validacao = models.DateTimeField(null=True, blank=True)
    validado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.analise.tipo} - {self.analise.paciente.nome}"

    def validar(self, usuario):
        self.validado = True
        self.data_validacao = timezone.now()
        self.validado_por = usuario
        self.save()

# Modelos para gestão de materiais e consumíveis

class Material(models.Model):
    nome = models.CharField(max_length=100)
    quantidade = models.PositiveIntegerField()
    estoque_minimo = models.PositiveIntegerField(default=10)  # Novo campo de limite mínimo
    validade = models.DateField()
    descricao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nome} --- estoque disponivel --> {self.quantidade} valido ate --> {self.validade}'


class Consumivel(models.Model):
    nome = models.CharField(max_length=100)
    quantidade = models.PositiveIntegerField()
    estoque_minimo = models.PositiveIntegerField(default=10)  # Novo campo de limite mínimo
    validade = models.DateField()
    descricao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nome} -- estoque disponivel {self.quantidade} --  valido ate {self.validade}'

# Modelos para gerenciamento de banco de sangue

class TipoSanguineo(models.Model):
    GRUPO_SANGUINEO_CHOICES = [
        ('a-', 'A-'), ('a+', 'A+'), ('b-', 'B-'), ('b+', 'B+'),
        ('ab-', 'AB-'), ('ab+', 'AB+'), ('o-', 'O-'), ('o+', 'O+')
    ]
    tipo = models.CharField(max_length=3, choices=GRUPO_SANGUINEO_CHOICES)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.tipo

class BancoDeSangue(models.Model):
    tipo_sanguineo = models.ForeignKey(TipoSanguineo, on_delete=models.CASCADE)
    quantidade_em_unidades = models.PositiveIntegerField()
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tipo_sanguineo.tipo} - {self.quantidade_em_unidades} Unidades"


class Auditoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=255)
    objeto_afetado = models.CharField(max_length=255)
    data_acao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} {self.acao} em {self.data_acao}"


