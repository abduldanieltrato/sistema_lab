# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Auditoria, Paciente, Analise, Material
from django.contrib.auth.models import User

@receiver(post_save, sender=Paciente)
@receiver(post_save, sender=Analise)
@receiver(post_save, sender=Material)
def registrar_criacao(sender, instance, created, **kwargs):
    acao = "criado" if created else "atualizado"
    Auditoria.objects.create(
        usuario=instance.usuario,  # ou modifique para o usuário que está logado
        acao=f"{sender.__name__} {acao}",
        objeto_afetado=str(instance)
    )

@receiver(post_delete, sender=Paciente)
@receiver(post_delete, sender=Analise)
@receiver(post_delete, sender=Material)
def registrar_exclusao(sender, instance, **kwargs):
    Auditoria.objects.create(
        usuario=instance.usuario,
        acao=f"{sender.__name__} excluído",
        objeto_afetado=str(instance)
    )
