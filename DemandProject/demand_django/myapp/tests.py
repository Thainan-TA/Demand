from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class LoginTestCase(TestCase):
    def setUp(self):
        self.credentials = {
            'cpf ou cnpj': 'testuser',
            'senha': 'secret'}
        User.objects.create_user(**self.credentials)

    def test_login(self):
        # Envia uma requisição POST com os dados de login
        response = self.client.post(reverse('login'), self.credentials, follow=True)
        
        # Verifica se o usuário foi autenticado e redirecionado
        self.assertTrue(response.context['user'].is_authenticated)
