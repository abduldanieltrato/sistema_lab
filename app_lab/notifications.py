from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings
from .models import Analise, Material, Consumivel
from django.utils import timezone
from celery import shared_task

# Configuração de Twilio
TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID  # Use as variáveis no settings.py
TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER = settings.TWILIO_PHONE_NUMBER

# Inicialização do cliente Twilio
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# Função de envio de e-mail
def enviar_email(destinatario, assunto, mensagem):
    send_mail(
        subject=assunto,
        message=mensagem,
        from_email='no-reply@clinica.com',  # E-mail configurado no settings
        recipient_list=[destinatario],
        fail_silently=False,
    )


# Função de envio de SMS
def enviar_sms(destinatario, mensagem):
    twilio_client.messages.create(
        body=mensagem,
        from_=TWILIO_PHONE_NUMBER,
        to=destinatario
    )


# Função genérica de notificação (analise, estoque, validade)
def notificar(destinatario_email, destinatario_sms, assunto, mensagem):
    enviar_email(destinatario_email, assunto, mensagem)
    enviar_sms(destinatario_sms, mensagem)


# Notificação de conclusão de análise
def notificar_analise_concluida(analise_id):
    analise = Analise.objects.get(id=analise_id)
    if analise.status == 'Concluída':
        mensagem = f"Sua análise '{analise.descricao}' foi concluída. Consulte o portal para ver o resultado."
        notificar(analise.paciente.email, analise.paciente.contacto, "Análise Concluída", mensagem)


# Função comum para verificar estoque ou validade
def verificar_item(consulta):
    itens_com_problema = []

    for item in consulta:
        if item.quantidade < item.estoque_minimo or (item.validade and (item.validade - timezone.now().date()).days <= 30):
            itens_com_problema.append(item.nome)

    return itens_com_problema


# Notificação de baixo estoque
def notificar_estoque_baixo():
    itens_com_baixo_estoque = []

    # Verifica estoque de materiais e consumíveis
    itens_com_baixo_estoque += verificar_item(Material.objects.all())
    itens_com_baixo_estoque += verificar_item(Consumivel.objects.all())

    if itens_com_baixo_estoque:
        mensagem = f"Alerta: estoque baixo para os itens: {', '.join(itens_com_baixo_estoque)}."
        notificar("responsavel@clinica.com", "+5599999999999", "Alerta de Estoque Baixo", mensagem)


# Notificação de validade próxima
def notificar_validade_proxima():
    itens_proximos_do_vencimento = []

    # Verifica validade de materiais e consumíveis
    itens_proximos_do_vencimento += verificar_item(Material.objects.all())
    itens_proximos_do_vencimento += verificar_item(Consumivel.objects.all())

    if itens_proximos_do_vencimento:
        mensagem = f"Alerta: itens próximos da validade: {', '.join(itens_proximos_do_vencimento)}."
        notificar("responsavel@clinica.com", "+5599999999999", "Alerta de Validade Próxima", mensagem)


@shared_task
def verificar_estoque():
    notificar_estoque_baixo()


@shared_task
def verificar_validade():
    notificar_validade_proxima()
