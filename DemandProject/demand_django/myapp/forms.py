from django import forms
from .models import Dados_Empresa, Dados_Colaborador, NovosContratantes
from django.contrib import admin
from django.contrib.auth.hashers import make_password

class LoginForm(forms.Form):
    cnpj_cpf = forms.CharField(max_length=14)
    senha = forms.CharField(widget=forms.PasswordInput)

class DadosEmpresaForm(forms.ModelForm):
    class Meta:
        model = Dados_Empresa
        fields = '__all__'

    def clean_senha(self):
        senha = self.cleaned_data.get('senha')
        return make_password(senha)

class DadosEmpresaAdmin(admin.ModelAdmin):
    form = DadosEmpresaForm

class DadosColaboradorForm(forms.ModelForm):
    class Meta:
        model = Dados_Colaborador
        fields = '__all__'

    def clean_senha(self):
        senha = self.cleaned_data.get('senha')
        return make_password(senha)

class DadosColaboradorAdmin(admin.ModelAdmin):
    form = DadosColaboradorForm


class UpgradePlanoForm(forms.Form):
    novo_plano = forms.ChoiceField(
        choices=Assinatura.PLANO_ESCOLHIDO_CHOICES,
        label='Novo Plano',
        required=True,
    )
    ativacao_imediata = forms.BooleanField(
        label='Ativação Imediata?',
        required=False,
        help_text='Se marcado, o novo plano será ativado imediatamente e o pagamento proporcional será cobrado.'
    )

class DowngradePlanoForm(forms.Form):
    novo_plano = forms.ChoiceField(
        choices=Assinatura.PLANO_ESCOLHIDO_CHOICES,
        label='Novo Plano',
        required=True,
    )

class PagamentoForm(forms.Form):
    comprovante_pagamento = forms.FileField(
        label='Comprovante de Pagamento',
        required=True,
        help_text='Faça upload do comprovante de pagamento para validar o pagamento da mensalidade.'
    )

class AssinaturaForm(forms.ModelForm):
    class Meta:
        model = Assinatura
        fields = [
            'IdEmpresa',
            'IdColaborador',
            'plano_escolhido',
            'status_assinatura',
        ]

class PagarMensalidadeForm(forms.Form):
    comprovante_pagamento = forms.FileField(required=False)

    def pagar_mensalidade(self, assinatura):
        comprovante = self.cleaned_data.get('comprovante_pagamento')
        assinatura.Mensalidade(assinatura).pagar(comprovante)

# class ComprovanteForm(forms.ModelForm):
#     class Meta:
#         model = Mensalidade
#         fields = ['comprovante_pagamento']
#         labels = {
#             'comprovante_pagamento': 'Comprovante de Pagamento',
#         }
#         help_texts = {
#             'comprovante_pagamento': 'Faça upload do comprovante de pagamento.',
#         }

class NovosContratantesForm(forms.ModelForm):
    class Meta:
        model = NovosContratantes
        fields = []

    # Métodos customizados para gerar, alterar e validar contratos
    def gerar_contrato(self):
        self.instance.gerar_contrato()

    def upload_contrato_assinado(self, arquivo):
        self.instance.upload_contrato_assinado(arquivo)

    def validar_contrato(self):
        self.instance.validar_contrato()

    def alterar_contrato(self):
        self.instance.alterar_contrato()

    def gerar_aditivo_contrato(self):
        self.instance.gerar_aditivo_contrato()
