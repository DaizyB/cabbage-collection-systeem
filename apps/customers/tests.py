from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomersTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='c1', password='pw')

    def test_address_create_requires_auth(self):
        self.client.login(username='c1', password='pw')
        resp = self.client.post(reverse('addresses'), {'address_text': '123 Main St'})
        self.assertEqual(resp.status_code, 201)
