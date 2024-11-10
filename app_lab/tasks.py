from .notifications import notificar_analise_concluida, notificar_estoque_baixo, notificar_validade_proxima
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Analise, Material, Consumivel, TipoSanguineo, BancoDeSangue, Resultado, Paciente


def enviar_alerta_por_email(subject, message, recipient='responsavel@exemplo.com'):
    """
    Função genérica para enviar alertas por e-mail.
    """
    send_mail(
        subject=subject,
        message=message,
        from_email="no-reply@clinica.com",
        recipient_list=[recipient],
        fail_silently=False,
    )


@shared_task
def enviar_email_analise_concluida(analise_id):
    """
    Envia um email para o paciente quando a análise é concluída.
    """
    try:
        analise = Analise.objects.get(id=analise_id)
        if analise.status == 'Concluída':
            enviar_alerta_por_email(
                subject="Sua análise está concluída!",
                message=f"Olá, sua análise '{analise.descricao}' foi concluída. Confira o resultado no portal.",
                recipient=analise.paciente.email
            )
            return f"E-mail enviado com sucesso para {analise.paciente.email}"
        else:
            return "A análise ainda não está concluída."
    except Analise.DoesNotExist:
        return "Análise não encontrada."


@shared_task
def verificar_estoque():
    """
    Verifica o estoque de materiais e consumíveis, enviando um alerta para itens abaixo do estoque mínimo.
    """
    items_com_baixo_estoque = []

    # Verifica o estoque de materiais e consumíveis
    for item in Material.objects.all() | Consumivel.objects.all():
        if item.quantidade < item.estoque_minimo:
            items_com_baixo_estoque.append(item.nome)

    if items_com_baixo_estoque:
        enviar_alerta_por_email(
            subject="Alerta de Baixa Quantidade de Estoque",
            message=f"Os seguintes itens estão com o estoque baixo: {', '.join(items_com_baixo_estoque)}"
        )


@shared_task
def verificar_validade():
    """
    Verifica a validade de materiais e consumíveis, enviando um alerta para itens próximos do vencimento.
    """
    items_proximos_do_vencimento = []
    data_atual = timezone.now().date()

    # Verifica validade de materiais e consumíveis
    for item in Material.objects.all() | Consumivel.objects.all():
        if item.validade and (item.validade - data_atual).days <= 30:
            items_proximos_do_vencimento.append(item.nome)

    if items_proximos_do_vencimento:
        enviar_alerta_por_email(
            subject="Alerta de Validade Próxima",
            message=f"Os seguintes itens estão próximos do vencimento: {', '.join(items_proximos_do_vencimento)}"
        )


@shared_task
def validar_resultados_pendentes():
    """
    Tarefa automática para validar os resultados de análise pendentes,
    conforme critérios específicos. Envia um e-mail ao responsável
    quando uma validação automática é realizada.
    """
    resultados_para_validar = Resultado.objects.filter(validado=False, analise__status='Concluída')

    for resultado in resultados_para_validar:
        # Critérios de validação (exemplo: se o resultado tiver um valor específico)
        if "critério específico" in resultado.valor:  # Altere conforme a lógica necessária
            resultado.validado = True
            resultado.data_validacao = timezone.now()
            resultado.validado_por = None  # Indica que foi uma validação automatizada
            resultado.save()

            # Notificação ao responsável pela validação automática
            enviar_email_validacao(resultado)


def enviar_email_validacao(resultado):
    """
    Envia um e-mail de notificação ao responsável pela validação automática.
    """
    send_mail(
        subject="Resultado de Análise Validado Automaticamente",
        message=(
            f"O resultado para a análise '{resultado.analise.tipo}' do paciente "
            f"{resultado.analise.paciente.nome} foi validado automaticamente.\n"
            f"Detalhes do resultado: {resultado.valor}\n"
            f"Data da validação: {resultado.data_validacao.strftime('%Y-%m-%d %H:%M:%S')}"
        ),
        from_email="no-reply@clinica.com",
        recipient_list=["responsavel@exemplo.com"],  # Altere para o e-mail do responsável
        fail_silently=False,
    )


@shared_task
def verificar_estoque():
    notificar_estoque_baixo()

@shared_task
def verificar_validade():
    notificar_validade_proxima()

@shared_task
def analise_concluida_task(analise_id):
    notificar_analise_concluida(analise_id)



