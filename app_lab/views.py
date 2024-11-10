# coding=utf-8
# views.py
import csv
import plotly.graph_objs as go
from .models import Auditoria
import datetime
import pandas as pd
from io import BytesIO
from weasyprint import HTML
from celery import shared_task
from .filters import PacienteFilter, AnaliseFilter, ConsumivelFilter, ResultadoFilter, MaterialFilter, BancoDeSangueFilter
from reportlab.pdfgen import canvas
from rest_framework import viewsets
from django.contrib import messages
from django.http import HttpResponse
from django.utils.timezone import now
from reportlab.lib.pagesizes import A4
from django.core.mail import EmailMessage
from .serializers import PacienteSerializer, AnaliseSerializer
from django.db.models.signals import post_migrate
from django.template.loader import render_to_string
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Paciente, Analise, Resultado, Material, Consumivel, BancoDeSangue
from .serializers import PacienteSerializer, AnaliseSerializer, ResultadoSerializer, MaterialSerializer, ConsumivelSerializer, BancoDeSangueSerializer
from .permissions import IsOwner, CanEditAnalise, CanEditResultado, CanEditMaterial, CanEditConsumivel, CanEditBancoDeSangue
from django.contrib.auth.decorators import login_required, permission_required
from .models import (
    Analise, Consumivel, Material, Paciente, Resultado, TipoSanguineo, BancoDeSangue
)
from .forms import (
    PacienteForm, AnaliseForm, ResultadoForm, MaterialForm, ConsumivelForm,
    TipoSanguineoForm, BancoDeSangueForm
)
from .utils import (
    relatorio_diario, relatorio_semanal, relatorio_mensal, relatorio_anual,
    relatorio_pacientes_diario, relatorio_pacientes_semanal, relatorio_pacientes_mensal, relatorio_pacientes_anual,
    relatorio_consumiveis_diario, relatorio_consumiveis_semanal, relatorio_consumiveis_mensal, relatorio_consumiveis_anual
)


# Criação dos Grupos e Permissões ao Migrar
@receiver(post_migrate)
def criar_grupos_e_permissoes(sender, **kwargs):
    grupos_permissoes = {
            "Recepcao": [
                    "add_paciente", "view_paciente", "add_analise", "view_analise",
                    "view_resultado", "print_resultado", "generate_basic_reports"
                    ],
            "Tecnico": [
                    "add_paciente", "view_paciente", "add_analise", "view_analise",
                    "view_resultado", "print_resultado", "generate_basic_reports",
                    "add_resultado", "change_resultado", "delete_resultado", "generate_detailed_reports"
                    ],
            "Administrador": [
                    "add_user", "change_user", "delete_user", "view_user",
                    "add_paciente", "change_paciente", "delete_paciente", "view_paciente",
                    "add_analise", "change_analise", "delete_analise", "view_analise",
                    "add_resultado", "change_resultado", "delete_resultado", "view_resultado",
                    "add_material", "change_material", "delete_material", "view_material",
                    "add_consumivel", "change_consumivel", "delete_consumivel", "view_consumivel",
                    "add_bancodesangue", "change_bancodesangue", "delete_bancodesangue", "view_bancodesangue",
                    "generate_detailed_reports"
                    ]
            }
    for grupo_nome, permissoes in grupos_permissoes.items():
        grupo, criado = Group.objects.get_or_create(name = grupo_nome)
        for perm_codename in permissoes:
            try:
                perm = Permission.objects.get(codename = perm_codename)
                grupo.permissions.add(perm)
            except Permission.DoesNotExist:
                print(f"Permissão '{perm_codename}' não encontrada!")


class MyAppConfig(AppConfig):
    name = 'lab_app'
    
    def ready(self):
        post_migrate.connect(criar_grupos_e_permissoes, sender = self)


# Views para Paciente
@login_required
@permission_required('app_lab.view_paciente', raise_exception = True)
def exportar_pacientes_csv(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename="pacientes.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nome', 'Data de Nascimento', 'Residencia', 'Nacionalidade', 'Genero', 'Contacto', 'Criado em'])
    pacientes = Paciente.objects.all()
    for paciente in pacientes:
        writer.writerow(
                [paciente.nome, paciente.data_nascimento, paciente.residencia, paciente.nacionalidade,
                 paciente.genero, paciente.contacto, paciente.criado_em]
                )
    return response


@login_required
@permission_required('app_lab.view_paciente', raise_exception = True)
def listar_pacientes(request):
    pacientes_list = Paciente.objects.all().order_by('-criado_em')
    paciente_filter = PacienteFilter(request.GET, queryset = pacientes_list)
    paginator = Paginator(paciente_filter.qs, 10)
    page_number = request.GET.get('page')
    pacientes = paginator.get_page(page_number)
    return render(request, 'pacientes/lista.html', {'pacientes': pacientes, 'filter': paciente_filter})


@login_required
@permission_required('app_lab.add_paciente', raise_exception = True)
def criar_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente criado com sucesso!')
            return redirect('listar_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'pacientes/form.html', {'form': form})


@login_required
@permission_required('app_lab.change_paciente', raise_exception = True)
def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk = pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance = paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('listar_pacientes')
    else:
        form = PacienteForm(instance = paciente)
    return render(request, 'pacientes/form.html', {'form': form})


@login_required
@permission_required('app_lab.delete_paciente', raise_exception = True)
def excluir_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk = pk)
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente apagado com sucesso!')
        return redirect('listar_pacientes')
    return render(request, 'pacientes/confirmar_exclusao.html', {'paciente': paciente})


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer


class PacienteListCreateView(generics.ListCreateAPIView):
    """
    View para listar todos os pacientes ou criar um novo paciente.
    """
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer


class PacienteRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    View para recuperar detalhes de um paciente específico ou atualizar suas informações.
    """
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer


class PacienteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer


@login_required
@permission_required('app_lab.view_paciente', raise_exception = True)
def relatorio_pacientes(request):
    contexto = {
            "relatorio_diario": relatorio_pacientes_diario(),
            "relatorio_semanal": relatorio_pacientes_semanal(),
            "relatorio_mensal": relatorio_pacientes_mensal(),
            "relatorio_anual": relatorio_pacientes_anual(),
            }
    return render(request, "core/relatorio_pacientes.html", contexto)


@login_required
@permission_required('app_lab.view_paciente', raise_exception = True)
def gerar_relatorio_pacientes(request):
    pacientes = Paciente.objects.all()
    html_string = render_to_string('relatorios/pacientes.html', {'pacientes': pacientes})
    pdf_file = HTML(string = html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type = 'application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_pacientes.pdf"'
    return response


@login_required
@permission_required('app_lab.view_paciente', raise_exception = True)
def gerar_relatorio_excel_pacientes(request):
    pacientes = Paciente.objects.all().values()
    df = pd.DataFrame(pacientes)
    response = HttpResponse(content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="relatorio_pacientes.xlsx"'
    with pd.ExcelWriter(response, engine = 'openpyxl') as writer:
        df.to_excel(writer, index = False, sheet_name = "Pacientes")
    return response


# Views para Consumivel
@login_required
@permission_required('app_lab.view_consumivel', raise_exception = True)
def listar_consumiveis(request):
    consumiveis = Consumivel.objects.all().order_by('-criado_em')
    paginator = Paginator(consumiveis, 10)
    page_number = request.GET.get('page')
    consumiveis_paginados = paginator.get_page(page_number)
    return render(request, 'consumiveis/lista.html', {'consumiveis': consumiveis_paginados})


@login_required
@permission_required('app_lab.add_consumivel', raise_exception = True)
def criar_consumivel(request):
    if request.method == 'POST':
        form = ConsumivelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consumível criado com sucesso!')
            return redirect('listar_consumiveis')
    else:
        form = ConsumivelForm()
    return render(request, 'consumiveis/form.html', {'form': form})


@login_required
@permission_required('app_lab.change_consumivel', raise_exception = True)
def editar_consumivel(request, pk):
    consumivel = get_object_or_404(Consumivel, pk = pk)
    if request.method == 'POST':
        form = ConsumivelForm(request.POST, instance = consumivel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consumível atualizado com sucesso!')
            return redirect('listar_consumiveis')
    else:
        form = ConsumivelForm(instance = consumivel)
    return render(request, 'consumiveis/form.html', {'form': form})


@login_required
@permission_required('app_lab.delete_consumivel', raise_exception = True)
def excluir_consumivel(request, pk):
    consumivel = get_object_or_404(Consumivel, pk = pk)
    if request.method == 'POST':
        consumivel.delete()
        messages.success(request, 'Consumível excluído com sucesso!')
        return redirect('listar_consumiveis')
    return render(request, 'consumiveis/confirmar_exclusao.html', {'consumivel': consumivel})


# Views para Analise
@login_required
@permission_required('app_lab.view_analise', raise_exception=True)
def listar_analises(request):
    analises = Analise.objects.all().order_by('-criado_em')
    paginator = Paginator(analises, 10)
    page_number = request.GET.get('page')
    analises_paginadas = paginator.get_page(page_number)
    return render(request, 'analises/lista.html', {'analises': analises_paginadas})

@login_required
@permission_required('app_lab.add_analise', raise_exception=True)
def criar_analise(request):
    if request.method == 'POST':
        form = AnaliseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Análise criada com sucesso!')
            return redirect('listar_analises')
    else:
        form = AnaliseForm()
    return render(request, 'analises/form.html', {'form': form})

@login_required
@permission_required('app_lab.change_analise', raise_exception=True)
def editar_analise(request, pk):
    analise = get_object_or_404(Analise, pk=pk)
    if request.method == 'POST':
        form = AnaliseForm(request.POST, instance=analise)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados da análise atualizados com sucesso!')
            return redirect('listar_analises')
    else:
        form = AnaliseForm(instance=analise)
    return render(request, 'analises/form.html', {'form': form})

@login_required
@permission_required('app_lab.delete_analise', raise_exception=True)
def excluir_analise(request, pk):
    analise = get_object_or_404(Analise, pk=pk)
    if request.method == 'POST':
        analise.delete()
        messages.success(request, 'Análise excluída com sucesso!')
        return redirect('listar_analises')
    return render(request, 'analises/confirmar_exclusao.html', {'analise': analise})


class AnaliseListCreateView(generics.ListCreateAPIView):
    """
    View para listar todas as análises ou criar uma nova análise.
    """
    queryset = Analise.objects.all()
    serializer_class = AnaliseSerializer


class AnaliseRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    View para recuperar detalhes de uma análise específica ou atualizar informações.
    """
    queryset = Analise.objects.all()
    serializer_class = AnaliseSerializer


class AnaliseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Analise.objects.all()
    serializer_class = AnaliseSerializer


# Views para Resultado
@login_required
@permission_required('app_lab.view_resultado', raise_exception=True)
def listar_resultados(request):
    resultados = Resultado.objects.all().order_by('-criado_em')
    paginator = Paginator(resultados, 10)
    page_number = request.GET.get('page')
    resultados_paginados = paginator.get_page(page_number)
    return render(request, 'resultados/lista.html', {'resultados': resultados_paginados})

@login_required
@permission_required('app_lab.add_resultado', raise_exception=True)
def criar_resultado(request):
    if request.method == 'POST':
        form = ResultadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resultado criado com sucesso!')
            return redirect('listar_resultados')
    else:
        form = ResultadoForm()
    return render(request, 'resultados/form.html', {'form': form})

@login_required
@permission_required('app_lab.change_resultado', raise_exception=True)
def editar_resultado(request, pk):
    resultado = get_object_or_404(Resultado, pk=pk)
    if request.method == 'POST':
        form = ResultadoForm(request.POST, instance=resultado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resultado atualizado com sucesso!')
            return redirect('listar_resultados')
    else:
        form = ResultadoForm(instance=resultado)
    return render(request, 'resultados/form.html', {'form': form})

@login_required
@permission_required('app_lab.delete_resultado', raise_exception=True)
def excluir_resultado(request, pk):
    resultado = get_object_or_404(Resultado, pk=pk)
    if request.method == 'POST':
        resultado.delete()
        messages.success(request, 'Resultado excluído com sucesso!')
        return redirect('listar_resultados')
    return render(request, 'resultados/confirmar_exclusao.html', {'resultado': resultado})


# Views para Material
@login_required
@permission_required('app_lab.view_material', raise_exception=True)
def listar_materiais(request):
    materiais = Material.objects.all().order_by('-criado_em')
    paginator = Paginator(materiais, 10)
    page_number = request.GET.get('page')
    materiais_paginados = paginator.get_page(page_number)
    return render(request, 'materiais/lista.html', {'materiais': materiais_paginados})

@login_required
@permission_required('app_lab.add_material', raise_exception=True)
def criar_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material criado com sucesso!')
            return redirect('listar_materiais')
    else:
        form = MaterialForm()
    return render(request, 'materiais/form.html', {'form': form})

@login_required
@permission_required('app_lab.change_material', raise_exception=True)
def editar_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material atualizado com sucesso!')
            return redirect('listar_materiais')
    else:
        form = MaterialForm(instance=material)
    return render(request, 'materiais/form.html', {'form': form})

@login_required
@permission_required('app_lab.delete_material', raise_exception=True)
def excluir_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material excluído com sucesso!')
        return redirect('listar_materiais')
    return render(request, 'materiais/confirmar_exclusao.html', {'material': material})


# Views para Consumivel
@login_required
@permission_required('app_lab.view_consumivel', raise_exception=True)
def listar_consumiveis(request):
    consumiveis = Consumivel.objects.all().order_by('-criado_em')
    paginator = Paginator(consumiveis, 10)
    page_number = request.GET.get('page')
    consumiveis_paginados = paginator.get_page(page_number)
    return render(request, 'consumiveis/lista.html', {'consumiveis': consumiveis_paginados})

@login_required
@permission_required('app_lab.add_consumivel', raise_exception=True)
def criar_consumivel(request):
    if request.method == 'POST':
        form = ConsumivelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consumível criado com sucesso!')
            return redirect('listar_consumiveis')
    else:
        form = ConsumivelForm()
    return render(request, 'consumiveis/form.html', {'form': form})

@login_required
@permission_required('app_lab.change_consumivel', raise_exception=True)
def editar_consumivel(request, pk):
    consumivel = get_object_or_404(Consumivel, pk=pk)
    if request.method == 'POST':
        form = ConsumivelForm(request.POST, instance=consumivel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consumível atualizado com sucesso!')
            return redirect('listar_consumiveis')
    else:
        form = ConsumivelForm(instance=consumivel)
    return render(request, 'consumiveis/form.html', {'form': form})

@login_required
@permission_required('app_lab.delete_consumivel', raise_exception=True)
def excluir_consumivel(request, pk):
    consumivel = get_object_or_404(Consumivel, pk=pk)
    if request.method == 'POST':
        consumivel.delete()
        messages.success(request, 'Consumível excluído com sucesso!')
        return redirect('listar_consumiveis')
    return render(request, 'consumiveis/confirmar_exclusao.html', {'consumivel': consumivel})


@login_required
@permission_required('app_lab.add_relatorio', raise_exception=True)
def enviar_relatorio_mensal(request):
    # Definir o período do mês atual
    hoje = now()
    inicio_mes = hoje.replace(day=1)
    fim_mes = (inicio_mes + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)

    # Consultar os dados do relatório mensal
    analises = Analise.objects.filter(criado_em__range=[inicio_mes, fim_mes])
    consumiveis = Consumivel.objects.filter(criado_em__range=[inicio_mes, fim_mes])
    materiais = Material.objects.filter(criado_em__range=[inicio_mes, fim_mes])
    pacientes = Paciente.objects.filter(criado_em__range=[inicio_mes, fim_mes])

    # Gerar o PDF do relatório
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.drawString(100, 800, f"Relatório Mensal - {hoje.strftime('%B %Y')}")
    p.drawString(100, 780, f"Data de Geração: {hoje.strftime('%d/%m/%Y')}")

    # Adicionar dados ao PDF
    y = 760
    p.drawString(100, y, "Resumo das Análises:")
    for analise in analises:
        y -= 20
        p.drawString(100, y, f"Análise {analise.id}: {analise.descricao} - {analise.status}")

    y -= 40
    p.drawString(100, y, "Resumo dos Consumíveis:")
    for consumivel in consumiveis:
        y -= 20
        p.drawString(100, y, f"Consumível {consumivel.id}: {consumivel.nome} - Quantidade: {consumivel.quantidade}")

    y -= 40
    p.drawString(100, y, "Resumo dos Materiais:")
    for material in materiais:
        y -= 20
        p.drawString(100, y, f"Material {material.id}: {material.nome} - Quantidade: {material.quantidade}")

    y -= 40
    p.drawString(100, y, "Resumo dos Pacientes:")
    for paciente in pacientes:
        y -= 20
        p.drawString(100, y, f"Paciente {paciente.id}: {paciente.nome} - Data de Nascimento: {paciente.data_nascimento}")

    # Finalizar o PDF
    p.showPage()
    p.save()

    # Enviar o PDF por email
    buffer.seek(0)
    email = EmailMessage(
        subject=f"Relatório Mensal - {hoje.strftime('%B %Y')}",
        body="Segue em anexo o relatório mensal.",
        from_email="abduld147@gmail.com",
        to=["abdultrato@gmail.com"],
    )
    email.attach(f"Relatorio_Mensal_{hoje.strftime('%B_%Y')}.pdf", buffer.getvalue(), "application/pdf")

    try:
        email.send()
        messages.success(request, "Relatório mensal enviado com sucesso!")
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao enviar o relatório: {e}")

    return redirect("pagina_inicial")

# Banco de Sangue
@login_required
@permission_required('app_lab.view_bancodesangue', raise_exception=True)
def listar_banco_de_sangue(request):
    banco_de_sangue = BancoDeSangue.objects.all().order_by('-criado_em')
    filtro = BancoDeSangueFilter(request.GET, queryset=banco_de_sangue)
    banco_de_sangue_filtrado = filtro.qs  # Filtrando os resultados

    paginator = Paginator(banco_de_sangue_filtrado, 10)
    page_number = request.GET.get('page')
    banco_de_sangue_paginado = paginator.get_page(page_number)

    return render(request, 'banco_de_sangue/lista.html', {
        'filtro': filtro,
        'banco_de_sangue': banco_de_sangue_paginado
    })


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated, IsOwner]  # Acesso apenas para o próprio paciente ou admin

class AnaliseViewSet(viewsets.ModelViewSet):
    queryset = Analise.objects.all()
    serializer_class = AnaliseSerializer
    permission_classes = [IsAuthenticated, CanEditAnalise]  # Acesso apenas para o paciente ou admin

class ResultadoViewSet(viewsets.ModelViewSet):
    queryset = Resultado.objects.all()
    serializer_class = ResultadoSerializer
    permission_classes = [IsAuthenticated, CanEditResultado]  # Acesso apenas para o paciente ou admin

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, CanEditMaterial]  # Acesso apenas para admins

class ConsumivelViewSet(viewsets.ModelViewSet):
    queryset = Consumivel.objects.all()
    serializer_class = ConsumivelSerializer
    permission_classes = [IsAuthenticated, CanEditConsumivel]  # Acesso apenas para admins

class BancoDeSangueViewSet(viewsets.ModelViewSet):
    queryset = BancoDeSangue.objects.all()
    serializer_class = BancoDeSangueSerializer
    permission_classes = [IsAuthenticated, CanEditBancoDeSangue]  # Acesso apenas para admins


def estoque_dashboard(request):
    # Dados de estoque de materiais
    materiais = Material.objects.all()
    consumiveis = Consumivel.objects.all()

    # Gráfico de materiais
    nomes_materiais = [m.nome for m in materiais]
    quantidades_materiais = [m.quantidade for m in materiais]
    fig_materiais = go.Figure([go.Bar(x=nomes_materiais, y=quantidades_materiais)])
    fig_materiais.update_layout(title='Estoque de Materiais', xaxis_title='Material', yaxis_title='Quantidade')

    # Gráfico de consumíveis
    nomes_consumiveis = [c.nome for c in consumiveis]
    quantidades_consumiveis = [c.quantidade for c in consumiveis]
    fig_consumiveis = go.Figure([go.Bar(x=nomes_consumiveis, y=quantidades_consumiveis)])
    fig_consumiveis.update_layout(title='Estoque de Consumíveis', xaxis_title='Consumível', yaxis_title='Quantidade')

    context = {
        'fig_materiais': fig_materiais.to_html(),
        'fig_consumiveis': fig_consumiveis.to_html(),
    }

    return render(request, 'dashboard.html', context)


def relatorio_auditoria(request):
    logs = Auditoria.objects.all().order_by('-data_acao')
    return render(request, 'relatorio_auditoria.html', {'logs': logs})
