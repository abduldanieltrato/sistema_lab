# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Define as configurações padrão do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_lab.settings')

app = Celery('sistema_lab')

# Carrega as configurações do Django para o Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente as tarefas em apps Django
app.autodiscover_tasks()

# Configuração para o Celery Beat Scheduler
app.conf.beat_schedule = {
    'verificar_estoque_diariamente': {
        'task': 'app_lab.tasks.verificar_estoque',
        'schedule': 86400.0,  # Executa diariamente (24 horas = 86400 segundos)
    },
    'verificar_validade_diariamente': {
        'task': 'app_lab.tasks.verificar_validade',
        'schedule': 86400.0,  # Executa diariamente
    },
}
