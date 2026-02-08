from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class AccountsTest(TestCase):
    def test_signup_flow(self):
        resp = self.client.post(reverse('signup'), {'username': 'u1', 'password1': 'strongpass123', 'password2': 'strongpass123'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(User.objects.filter(username='u1').exists())
