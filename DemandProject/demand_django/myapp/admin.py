from django.contrib import admin
from .models import Dados_Empresa, Dados_Colaborador, NovosContratantes
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Sum


admin.site.register(Dados_Empresa)
admin.site.register(Dados_Colaborador)
admin.site.register(NovosContratantes)