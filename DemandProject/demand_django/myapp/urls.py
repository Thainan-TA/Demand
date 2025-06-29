from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views
from .views import DadosEmpresaViewSet, DadosColaboradorViewSet, NovosContratantesViewSet

router = DefaultRouter()
router.register(r'dados_empresa', DadosEmpresaViewSet)
router.register(r'dados_colaborador', DadosColaboradorViewSet)
router.register(r'novoscontratantes', NovosContratantesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login_view, name='login'),
    path('perfil-cnpj/', views.perfil_view, name='perfil-cnpj'),
    path('perfil-cpf/', views.perfil_view, name='perfil-cpf'),
    path('logout/', views.logout_view, name='logout'),
    path('novoscontratantes/', views.novosContratantes_view, name='novoscontratantes'),
    
]

