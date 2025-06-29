from rest_framework import viewsets, status
from .models import Dados_Empresa, Dados_Colaborador, NovosContratantes
from .serializers import DadosEmpresaSerializer, DadosColaboradorSerializer, NovosContratantesSerializer
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import LoginForm, UpgradePlanoForm, NovosContratantesForm
from django.contrib.auth.backends import get_user_model
from django.conf import settings
from django.views.generic import ListView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.urls import reverse
from rest_framework.decorators import action
from django.core.mail import send_mail
from reportlab.pdfgen import canvas
from io import BytesIO
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
from django.http import Http404, HttpResponseBadRequest
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect


# ViewSets para API
class DadosEmpresaViewSet(viewsets.ModelViewSet):
    queryset = Dados_Empresa.objects.all()
    serializer_class = DadosEmpresaSerializer

class DadosColaboradorViewSet(viewsets.ModelViewSet):
    queryset = Dados_Colaborador.objects.all()
    serializer_class = DadosColaboradorSerializer

class NovosContratantesViewSet(viewsets.ModelViewSet):
    queryset = NovosContratantes.objects.all()
    serializer_class = NovosContratantesSerializer

@csrf_exempt
def login_view(request):
    error_message = None
    if request.method == 'POST':
        cnpj_cpf = request.POST.get('CnpjCpf')
        senha = request.POST.get('Senha')

        # Tenta autenticar como empresa
        user = authenticate(request, username=cnpj_cpf, password=senha)
        if user is not None and hasattr(user, 'dados_empresa'):
            login(request, user)
            request.session['user_id'] = user.id
            request.session['user_type'] = 'empresa'
            return redirect('perfil-cnpj')  # Redireciona para perfil-cnpj.html

        # Autentica diretamente como empresa
        try:
            empresa = Dados_Empresa.objects.get(cnpj=cnpj_cpf)
            if check_password(senha, empresa.senha_login_empresa):
                user = empresa
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session['user_id'] = user.cnpj
                request.session['user_type'] = 'empresa'
                return redirect('perfil-cnpj')
            else:
                error_message = "Senha incorreta ou usuário não encontrado."
        except Dados_Empresa.DoesNotExist:
            pass
        
        user = authenticate(request, username=cnpj_cpf, password=senha)
        if user is not None and hasattr(user, 'dados_colaborador'):
            login(request, user)
            request.session['user_id'] = user.id
            request.session['user_type'] = 'colaborador'
            return redirect('perfil-cpf')  # Redireciona para perfil-cnpj.html
        # Tenta autenticar como colaborador
        try:
            colaborador = Dados_Colaborador.objects.get(cpf=cnpj_cpf)
            if check_password(senha, colaborador.senha_login_colaborador):
                user = colaborador
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session['user_id'] = user.cpf
                request.session['user_type'] = 'colaborador'
                return redirect('perfil-cpf')  # Redireciona para perfil-cpf.html
            else:
                error_message = "Senha incorreta ou usuário não encontrado."
        except Dados_Colaborador.DoesNotExist:
            error_message = "CNPJ/CPF ou senha inválidos."

    return render(request, 'login.html', {'error_message': error_message})

@login_required
def perfil_view(request):
    user = request.user
    usuario_empresa = None
    usuario_colaborador = None
    template = 'perfil.html'  # Valor padrão, mas será alterado conforme o tipo de usuário

    try:
        # Verifica o tipo de usuário e define o template correto
        if hasattr(user, 'dados_empresa'):
            usuario_empresa = user.dados_empresa
            template = 'perfil-cnpj.html'
        elif hasattr(user, 'dados_colaborador'):
            usuario_colaborador = user.dados_colaborador
            template = 'perfil-cpf.html'

        if request.method == 'POST':
            # Atualiza campos para empresas
            if usuario_empresa:
                usuario_empresa.cnpj = request.POST.get('cnpj', usuario_empresa.cnpj)
                usuario_empresa.razao_social = request.POST.get('razao_social', usuario_empresa.razao_social)
                usuario_empresa.nome_fantasia = request.POST.get('nome_fantasia', usuario_empresa.nome_fantasia)
                usuario_empresa.endereco_comercial = request.POST.get('endereco_comercial', usuario_empresa.endereco_comercial)
                usuario_empresa.email_corporativo = request.POST.get('email_corporativo', usuario_empresa.email_corporativo)
                usuario_empresa.celular_whatsapp = request.POST.get('celular_whatsapp', usuario_empresa.celular_whatsapp)
                usuario_empresa.save()

            # Atualiza campos para colaboradores
            elif usuario_colaborador:
                usuario_colaborador.cpf = request.POST.get('cpf', usuario_colaborador.cpf)
                usuario_colaborador.nome = request.POST.get('nome', usuario_colaborador.nome)
                usuario_colaborador.cargo = request.POST.get('cargo', usuario_colaborador.cargo)
                usuario_colaborador.email_corporativo = request.POST.get('email_corporativo', usuario_colaborador.email_corporativo)
                usuario_colaborador.celular_whatsapp = request.POST.get('celular_whatsapp', usuario_colaborador.celular_whatsapp)
                usuario_colaborador.save()

            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')

    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao salvar o perfil: {e}')
        
    # Renderiza o perfil com o template específico
    return render(request, template, {'usuario_empresa': usuario_empresa, 'usuario_colaborador': usuario_colaborador})

def novosContratantes_view(request):
    """
    View para registrar um novo contratante usando template HTML.
    """
    
    if request.method == 'POST':
        # Obtenha os dados enviados no formulário
        status = request.POST.get('status')
        nome_empresa = request.POST.get('nome_empresa')
        nome_fantasia = request.POST.get('nome_fantasia')
        telefone_corporativo = request.POST.get('telefone_corporativo')
        cnpj = request.POST.get('cnpj')
        endereco_comercial = request.POST.get('endereco_comercial')
        email_corporativo = request.POST.get('email_corporativo')
        cpf = request.POST.get('cpf')
        nome_completo = request.POST.get('nome_completo')
        nome_social = request.POST.get('nome_social')
        nome_exibicao = request.POST.get('nome_exibicao')
        cargo = request.POST.get('cargo')
        telefone_pessoal = request.POST.get('telefone_pessoal')
        email_pessoal = request.POST.get('email_pessoal')

        # Salve os dados no banco de dados
        NovosContratantes = NovosContratantes(
            status=status,
            nome_empresa=nome_empresa,
            nome_fantasia=nome_fantasia,
            telefone_corporativo=telefone_corporativo,
            cnpj=cnpj,
            endereco_comercial=endereco_comercial,
            email_corporativo=email_corporativo,
            cpf=cpf,
            nome_completo=nome_completo,
            nome_social=nome_social,
            nome_exibicao=nome_exibicao,
            cargo=cargo,
            telefone_pessoal=telefone_pessoal,
            email_pessoal=email_pessoal
        )
        NovosContratantes.save()

        # Redirecione ou exiba uma mensagem de sucesso
        return render(request, "novoscontratantes.html", {"success_message": "Novos contratantes registrado com sucesso!"})
    
    # Para requisições GET, apenas renderize o template
    if request.method == 'GET':
        return render(request, "novoscontratantes.html")
    
    # Caso o método seja diferente de GET ou POST, retorne um erro
    return HttpResponse("Método inválido.", status=405)


class NovosContratantesViewSet(viewsets.ModelViewSet):
    queryset = NovosContratantes.objects.all()
    serializer_class = NovosContratantesSerializer

    @action(detail=True, methods=['post'])
    def gerar_contrato(self, request, pk=None):
        lead = self.get_object()
        lead.gerar_contrato()
        return Response({'status': 'Contrato gerado'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def upload_contrato_assinado(self, request, pk=None):
        lead = self.get_object()
        arquivo = request.FILES.get('arquivo')
        lead.upload_contrato_assinado(arquivo)
        return Response({'status': 'Contrato assinado enviado'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def validar_contrato(self, request, pk=None):
        lead = self.get_object()
        lead.validar_contrato()
        return Response({'status': 'Contrato validado e lead transformado em cliente'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def alterar_contrato(self, request, pk=None):
        lead = self.get_object()
        try:
            lead.alterar_contrato()
            return Response({'status': 'Contrato alterado'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def gerar_aditivo_contrato(self, request, pk=None):
        lead = self.get_object()
        lead.gerar_aditivo_contrato()
        return Response({'status': 'Aditivo de contrato gerado'}, status=status.HTTP_200_OK)

@login_required
def logout_view(request):
    # Encerra a sessão do usuário
    logout(request)
    # Redireciona para a página de login
    return redirect('login')
