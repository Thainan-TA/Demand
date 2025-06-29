import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demand_django.settings')
django.setup()

# Agora você pode importar seus modelos ou executar outros comandos Django
from myapp.models import Dados_Empresa, Dados_Colaborador, NovosContratantes

# Exemplo de operação com os modelos
print(Dados_Empresa.objects.all())
print(Dados_Colaborador.objects.all())
print(NovosContratantes.objects.all())