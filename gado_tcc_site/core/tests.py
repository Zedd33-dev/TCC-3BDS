from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .forms import MovementForm, VaccinationForm
from .models import Animal, Farm, HerdGroup


class SmokeTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='12345')
        self.client.login(username='tester', password='12345')

    def test_create_animal(self):
        farm = Farm.objects.create(name='Fazenda X')
        animal = Animal.objects.create(farm=farm, ear_tag='BR9999', sex='M')
        self.assertEqual(animal.ear_tag, 'BR9999')

    def test_dashboard_authenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class FormValidationTest(TestCase):
    def test_vaccination_next_due_before_date_invalid(self):
        farm = Farm.objects.create(name='Fazenda Y')
        animal = Animal.objects.create(farm=farm, ear_tag='BR1234', sex='F')
        form = VaccinationForm(data={
            'animal': animal.id,
            'vaccine': 'Aftosa',
            'date': '2026-02-10',
            'next_due': '2026-02-01',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('next_due', form.errors)

    def test_movement_same_group_invalid(self):
        farm = Farm.objects.create(name='Fazenda Z')
        group = HerdGroup.objects.create(farm=farm, name='Lote A')
        animal = Animal.objects.create(farm=farm, group=group, ear_tag='BR5555', sex='M')
        form = MovementForm(data={
            'animal': animal.id,
            'from_group': group.id,
            'to_group': group.id,
            'date': date.today(),
            'reason': 'Teste',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('to_group', form.errors)
