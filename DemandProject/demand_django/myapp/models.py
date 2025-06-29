from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.core.files import File
from django.conf import settings
from io import BytesIO
import reportlab
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from django.conf import settings
import requests
from django.template.loader import render_to_string
import requests
from django.db.models import JSONField
from django.conf import settings
from decimal import Decimal
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User

def validate_password(value):
    if not (7 <= len(value) <= 21):
        raise ValidationError('A senha deve ter entre 7 e 21 caracteres.')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('A senha deve conter pelo menos uma letra maiúscula.')
    if not re.search(r'[a-z]', value):
        raise ValidationError('A senha deve conter pelo menos uma letra minúscula.')
    if not re.search(r'[0-9]', value):
        raise ValidationError('A senha deve conter pelo menos um número.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('A senha deve conter pelo menos um caractere especial.')

# Validador para restringir números repetidos em sequência
def validate_repeated_numbers(value):
    # Verifica se há mais de 3 números consecutivos repetidos
    if re.search(r"(\d)\1{3,}", value):
        raise ValidationError("O campo não pode conter mais de 3 números repetidos em sequência.")

# Validador que permite apenas números
numeric_validator = RegexValidator(r'^[0-9]*$', 'Este campo aceita apenas números.')

class EmpresaManager(BaseUserManager):
    def create_user(self, cnpj, password=None, **extra_fields):
        if not cnpj:
            raise ValueError('O CNPJ deve ser definido')
        empresa = self.model(cnpj=cnpj, **extra_fields)
        if password:
            empresa.set_password(password)
        empresa.save(using=self._db)
        return empresa

class ColaboradorManager(BaseUserManager):
    def create_user(self, cpf, password=None, **extra_fields):
        if not cpf:
            raise ValueError('O CPF deve ser definido')
        colaborador = self.model(cpf=cpf, **extra_fields)
        if password:
            colaborador.set_password(password)
        colaborador.save(using=self._db)
        return colaborador

class Dados_Empresa(AbstractBaseUser):
    EMPRESA_ASSINANTES_CHOICES = [
        ('mvp', 'Mvp'),
        ('vitrine', 'Vitrine'),
        ('startup', 'Startup'),
        ('business','Business'),
    ]

    IdEmpresa = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    cnpj = models.CharField(max_length=18, unique=True, validators=[numeric_validator, validate_repeated_numbers])
    razao_social = models.CharField(max_length=100)
    nome_fantasia = models.CharField(max_length=100)
    endereco_comercial = models.CharField(max_length=255)
    email_corporativo = models.EmailField(max_length=100)
    senha_login_empresa = models.CharField(max_length=200, validators=[validate_password])
    telefone_fixo = models.CharField(max_length=20, validators=[numeric_validator])
    email_google_agenda = models.EmailField(max_length=100, blank=True, null=True)
    celular_whatsapp = models.CharField(max_length=20, blank=True, null=True, validators=[numeric_validator])
    tipo_assinante_Empresa = models.CharField(max_length=25, choices=EMPRESA_ASSINANTES_CHOICES)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = EmpresaManager()

    USERNAME_FIELD = 'cnpj'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if self.senha_login_empresa and not self.senha_login_empresa.startswith('pbkdf1_'):
            self.senha_login_empresa = make_password(self.senha_login_empresa)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_fantasia
    

class Dados_Colaborador(AbstractBaseUser):
    COLABORADOR_ASSINANTES_CHOICES = [
        ('mvp', 'Mvp'),
        ('vitrine', 'Vitrine'),
        ('startup', 'Startup'),
        ('business','Business'),
    ]

    IdColaborador = models.AutoField(primary_key=True)
    Id_Empresa = models.ForeignKey(Dados_Empresa, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, validators=[numeric_validator, validate_repeated_numbers])
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50)
    email_corporativo = models.EmailField(max_length=100)
    celular_whatsapp = models.CharField(max_length=20, validators=[numeric_validator])
    senha_login_colaborador = models.CharField(max_length=255, validators=[validate_password])
    telefone_fixo = models.CharField(max_length=20, validators=[numeric_validator])
    tipo_assinante_Colaborador = models.CharField(max_length=25, choices=COLABORADOR_ASSINANTES_CHOICES)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = ColaboradorManager()

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if self.senha_login_colaborador and not self.senha_login_colaborador.startswith('pbkdf2_'):
            self.senha_login_colaborador = make_password(self.senha_login_colaborador)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class NovosContratantes(models.Model):
    CONTRATANTES_STATUS_CHOICES = [
        ('frio', 'Frio'),
        ('morno', 'Morno'),
        ('quente', 'Quente'),
    ]
    
    IdLead = models.AutoField(primary_key=True)
    status = models.CharField(max_length=10, choices=CONTRATANTES_STATUS_CHOICES)
    nome_empresa = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, validators=[numeric_validator, validate_repeated_numbers])
    endereco_comercial = models.CharField(max_length=255, default='')
    email_corporativo = models.EmailField(default='')
    cpf = models.CharField(max_length=14, unique=True, validators=[numeric_validator, validate_repeated_numbers])
    nome_fantasia = models.CharField(max_length=100, default='')
    telefone_corporativo = models.CharField(max_length=20, validators=[numeric_validator], default='')
    nome_completo = models.CharField(max_length=100, null=True)
    nome_social = models.CharField(max_length=100, null=True)
    nome_exibicao = models.CharField(max_length=100, null=True)
    cargo = models.CharField(max_length=100, null=True)
    telefone_pessoal = models.CharField(max_length=20, validators=[numeric_validator], default='')
    email_pessoal = models.EmailField(default='email@default.com')
    website = models.URLField(blank=True, null=True)
    perfil_linkedin = models.URLField(blank=True, null=True)
    instagram = models.CharField(max_length=50, blank=True, null=True)
    link_youtube = models.URLField(blank=True, null=True)
    historico_abordagem = models.TextField()
    contrato = models.FileField(upload_to='contratos/', blank=True, null=True)
    contrato_assinado = models.FileField(upload_to='contratos_assinados/', blank=True, null=True)
    contrato_validado = models.BooleanField(default=False)
    aditivo_contrato = models.FileField(upload_to='aditivos_contratos/', blank=True, null=True)

    def __str__(self):
        return self.nome_empresa
    
    