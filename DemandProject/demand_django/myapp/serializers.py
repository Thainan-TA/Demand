from rest_framework import serializers
from .models import Dados_Empresa, Dados_Colaborador, NovosContratantes

class DadosEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dados_Empresa
        fields = '__all__'

class DadosColaboradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dados_Colaborador
        fields = '__all__'

class NovosContratantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NovosContratantes
        fields = [
            'IdLead',
            'status',
            'nome_empresa',
            'cnpj',
            'cpf',
            'nome_contato',
            'telefone',
            'email',
            'website',
            'perfil_linkedin',
            'instagram',
            'link_youtube',
            'historico_abordagem',
            'contrato',
            'contrato_assinado',
            'contrato_validado',
            'aditivo_contrato',
        ]

    # Métodos customizados para ações específicas
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
