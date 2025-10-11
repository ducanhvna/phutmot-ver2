from django.test import TestCase
from .models import Customer

class CustomerModelTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            username='testuser',
            phone_number='1234567890',
            id_card_number='ID123456',
            old_id_card_number='OLDID123456',
            name='Test User',
            english_name='Test User EN',
            verification_status=True
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.username, 'testuser')
        self.assertEqual(self.customer.phone_number, '1234567890')
        self.assertEqual(self.customer.id_card_number, 'ID123456')
        self.assertEqual(self.customer.old_id_card_number, 'OLDID123456')
        self.assertEqual(self.customer.name, 'Test User')
        self.assertEqual(self.customer.english_name, 'Test User EN')
        self.assertTrue(self.customer.verification_status)

    def test_customer_str(self):
        self.assertEqual(str(self.customer), 'testuser')  # Assuming __str__ method returns username

    def test_customer_verification_status(self):
        self.customer.verification_status = False
        self.customer.save()
        self.assertFalse(self.customer.verification_status)