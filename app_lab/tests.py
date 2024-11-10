from django.test import TestCase
from .models import Paciente
from django.urls import reverse


class PacienteTestCase(TestCase):
    def setUp(self):
        Paciente.objects.create(nome = "João Silva", data_nascimento = "1990-01-01")
    
    def test_paciente_criado_com_sucesso(self):
        joao = Paciente.objects.get(nome = "João Silva")
        self.assertEqual(joao.nome, "João Silva")
        self.assertEqual(joao.data_nascimento.strftime("%Y-%m-%d"), "1990-01-01")
