from django.test import TestCase
from django.utils import timezone
from .models import Farm, Animal

class SmokeTest(TestCase):
    def test_create_animal(self):
        f = Farm.objects.create(name="Fazenda X")
        a = Animal.objects.create(farm=f, ear_tag="BR9999", sex="M")
        self.assertEqual(a.ear_tag, "BR9999")
