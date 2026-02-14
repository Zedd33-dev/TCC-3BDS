from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class Farm(models.Model):
    name = models.CharField(max_length=120)
    owner_name = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=2, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Pasture(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='pastures')
    name = models.CharField(max_length=120)
    area_ha = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.farm} — {self.name}"

class HerdGroup(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=120)
    pasture = models.ForeignKey(Pasture, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.farm} — {self.name}"

class Animal(models.Model):
    class Sex(models.TextChoices):
        MALE = 'M', 'Macho'
        FEMALE = 'F', 'Fêmea'

    class Status(models.TextChoices):
        ACTIVE = 'ATIVO', 'Ativo'
        SOLD = 'VENDIDO', 'Vendido'
        DEAD = 'MORTO', 'Morto'
        LOST = 'PERDIDO', 'Perdido'

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='animals')
    group = models.ForeignKey(HerdGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='animals')
    ear_tag = models.CharField(max_length=40, unique=True)  # brinco / identificação
    name = models.CharField(max_length=120, blank=True)
    breed = models.CharField(max_length=120, blank=True)
    sex = models.CharField(max_length=1, choices=Sex.choices)
    birth_date = models.DateField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.ear_tag} — {self.name or 'Sem nome'}"

    def clean(self):
        if self.group and self.group.farm_id != self.farm_id:
            raise ValidationError({'group': 'O lote precisa pertencer à mesma fazenda do animal.'})

class WeightRecord(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='weights')
    date = models.DateField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

class Vaccination(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine = models.CharField(max_length=120)
    dose = models.CharField(max_length=60, blank=True)
    date = models.DateField()
    next_due = models.DateField(null=True, blank=True)
    veterinarian = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

class Treatment(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='treatments')
    kind = models.CharField(max_length=120)  # vermífugo, antibiótico etc
    product = models.CharField(max_length=120, blank=True)
    date = models.DateField()
    next_due = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

class Movement(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='movements')
    from_group = models.ForeignKey(HerdGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='moves_from')
    to_group = models.ForeignKey(HerdGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='moves_to')
    date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date']

    def clean(self):
        errors = {}

        if not self.from_group and not self.to_group:
            errors['to_group'] = 'Informe ao menos um lote de origem ou destino.'

        if self.from_group_id and self.to_group_id and self.from_group_id == self.to_group_id:
            errors['to_group'] = 'Os lotes de origem e destino não podem ser iguais.'

        for field_name in ('from_group', 'to_group'):
            group = getattr(self, field_name)
            if group and self.animal_id and group.farm_id != self.animal.farm_id:
                errors[field_name] = 'O lote deve ser da mesma fazenda do animal selecionado.'

        if errors:
            raise ValidationError(errors)

class Sale(models.Model):
    animal = models.OneToOneField(Animal, on_delete=models.CASCADE, related_name='sale')
    date = models.DateField()
    buyer = models.CharField(max_length=160)
    price_brl = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    def clean(self):
        if self.price_brl is not None and self.price_brl <= 0:
            raise ValidationError({'price_brl': 'O valor da venda deve ser maior que zero.'})

class CostEntry(models.Model):
    class Category(models.TextChoices):
        FEED = 'RACAO', 'Ração'
        VACCINE = 'VACINA', 'Vacina'
        MEDICINE = 'MEDICAMENTO', 'Medicamento'
        LABOR = 'MAO_DE_OBRA', 'Mão de obra'
        OTHER = 'OUTROS', 'Outros'

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='costs')
    date = models.DateField()
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.CharField(max_length=200)
    amount_brl = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['-date']
