from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Animal, Farm, HerdGroup, Movement, Sale


class SmokeTest(TestCase):
    def test_create_animal(self):
        farm = Farm.objects.create(name="Fazenda X")
        animal = Animal.objects.create(farm=farm, ear_tag="BR9999", sex="M")
        self.assertEqual(animal.ear_tag, "BR9999")


class AnimalValidationTest(TestCase):
    def test_animal_group_must_belong_to_same_farm(self):
        farm_a = Farm.objects.create(name="Fazenda A")
        farm_b = Farm.objects.create(name="Fazenda B")
        group_b = HerdGroup.objects.create(farm=farm_b, name="Lote B")

        animal = Animal(
            farm=farm_a,
            group=group_b,
            ear_tag="BR1001",
            sex=Animal.Sex.MALE,
        )

        with self.assertRaises(ValidationError):
            animal.full_clean()


class MovementValidationTest(TestCase):
    def setUp(self):
        self.farm = Farm.objects.create(name="Fazenda Única")
        self.other_farm = Farm.objects.create(name="Fazenda Externa")
        self.animal = Animal.objects.create(
            farm=self.farm,
            ear_tag="BR2001",
            sex=Animal.Sex.FEMALE,
        )
        self.group_a = HerdGroup.objects.create(farm=self.farm, name="Lote A")
        self.group_b = HerdGroup.objects.create(farm=self.farm, name="Lote B")
        self.group_other = HerdGroup.objects.create(farm=self.other_farm, name="Lote Externo")

    def test_requires_origin_or_destination(self):
        movement = Movement(animal=self.animal, date=date(2026, 2, 10))
        with self.assertRaises(ValidationError):
            movement.full_clean()

    def test_disallows_same_origin_and_destination(self):
        movement = Movement(
            animal=self.animal,
            from_group=self.group_a,
            to_group=self.group_a,
            date=date(2026, 2, 10),
        )
        with self.assertRaises(ValidationError):
            movement.full_clean()

    def test_disallows_group_from_another_farm(self):
        movement = Movement(
            animal=self.animal,
            to_group=self.group_other,
            date=date(2026, 2, 10),
        )
        with self.assertRaises(ValidationError):
            movement.full_clean()

    def test_movement_updates_animal_group(self):
        self.animal.group = self.group_a
        self.animal.save(update_fields=["group"])

        movement = Movement.objects.create(
            animal=self.animal,
            from_group=self.group_a,
            to_group=self.group_b,
            date=date(2026, 2, 11),
        )

        self.animal.refresh_from_db()
        self.assertEqual(self.animal.group_id, self.group_b.id)
        self.assertEqual(movement.to_group_id, self.group_b.id)


class SaleValidationTest(TestCase):
    def test_sale_price_must_be_positive(self):
        farm = Farm.objects.create(name="Fazenda Venda")
        animal = Animal.objects.create(farm=farm, ear_tag="BR3001", sex=Animal.Sex.MALE)

        sale = Sale(animal=animal, date=date(2026, 2, 10), buyer="Comprador", price_brl=Decimal("0.00"))

        with self.assertRaises(ValidationError):
            sale.full_clean()
