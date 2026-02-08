from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.customers.models import Address

User = get_user_model()


class EndToEndTest(TestCase):
    def test_signup_address_pickup_admin(self):
        # Signup
        resp = self.client.post(reverse('signup'), {'username': 'e2euser', 'password1': 'strongpass123', 'password2': 'strongpass123'})
        self.assertEqual(resp.status_code, 200)
        # Login as user
        self.client.login(username='e2euser', password='strongpass123')
        user = User.objects.get(username='e2euser')
        # Create address
        resp = self.client.post(reverse('addresses'), {'address_text': '100 Test Ave'})
        self.assertEqual(resp.status_code, 201)
        addr = Address.objects.filter(user=user).first()
        # Schedule pickup
        resp = self.client.post(reverse('schedule-pickup'), {'address': addr.id, 'scheduled_time': '2030-01-01T00:00:00Z'})
        self.assertEqual(resp.status_code, 201)
        # Admin view requires staff; create staff user and check dashboard loads
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'adminpw')
        self.client.login(username='admin', password='adminpw')
        resp = self.client.get(reverse('admin-dashboard'))
        self.assertIn(resp.status_code, (200, 302))
