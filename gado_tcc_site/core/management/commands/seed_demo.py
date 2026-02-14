from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

from core.models import Farm, Pasture, HerdGroup, Animal, WeightRecord, Vaccination, Treatment, Movement, CostEntry

User = get_user_model()

BREEDS = ["Nelore", "Angus", "Brahman", "Guzerá", "Gir", "Senepol", "Tabapuã"]
VACC = ["Aftosa", "Brucelose", "Clostridioses", "Raiva", "IBR/BVD"]
TRT = [("Vermífugo","Ivermectina"), ("Antibiótico","Oxitetraciclina"), ("Carrapaticida","Fluazuron")]

class Command(BaseCommand):
    help = "Cria dados demo para apresentação do TCC."

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="demo").exists():
            User.objects.create_user(username="demo", password="demo12345")
            self.stdout.write(self.style.SUCCESS("Usuário demo criado: demo / demo12345"))

        farm, _ = Farm.objects.get_or_create(name="Fazenda Modelo", defaults={
            "owner_name": "Produtor Exemplo",
            "city": "Cidade Exemplo",
            "state": "SP",
        })
        p1, _ = Pasture.objects.get_or_create(farm=farm, name="Piquete 1", defaults={"area_ha": 12.5})
        p2, _ = Pasture.objects.get_or_create(farm=farm, name="Piquete 2", defaults={"area_ha": 9.0})
        g1, _ = HerdGroup.objects.get_or_create(farm=farm, name="Lote A", defaults={"pasture": p1})
        g2, _ = HerdGroup.objects.get_or_create(farm=farm, name="Lote B", defaults={"pasture": p2})

        # animais
        for n in range(1, 31):
            tag = f"BR{1000+n}"
            a, created = Animal.objects.get_or_create(
                ear_tag=tag,
                defaults={
                    "farm": farm,
                    "group": random.choice([g1, g2]),
                    "name": f"Animal {n}",
                    "breed": random.choice(BREEDS),
                    "sex": random.choice(["M","F"]),
                    "birth_date": timezone.localdate() - timedelta(days=random.randint(200, 1200)),
                    "purchase_date": timezone.localdate() - timedelta(days=random.randint(30, 700)),
                    "status": "ATIVO",
                }
            )
            if created:
                start = (a.birth_date or timezone.localdate() - timedelta(days=600)) + timedelta(days=120)
                w = random.randint(160, 240)
                for k in range(random.randint(5, 10)):
                    d = start + timedelta(days=60*k)
                    w += random.randint(8, 22)
                    WeightRecord.objects.create(animal=a, date=d, weight_kg=w)

                for k in range(random.randint(2, 5)):
                    d = timezone.localdate() - timedelta(days=random.randint(10, 400))
                    next_due = d + timedelta(days=random.choice([180, 365]))
                    Vaccination.objects.create(animal=a, vaccine=random.choice(VACC), dose=random.choice(["1ª dose","Reforço",""]),
                                              date=d, next_due=next_due)

                if random.random() < 0.6:
                    kind, prod = random.choice(TRT)
                    d = timezone.localdate() - timedelta(days=random.randint(10, 300))
                    next_due = d + timedelta(days=random.choice([90, 120, 180]))
                    Treatment.objects.create(animal=a, kind=kind, product=prod, date=d, next_due=next_due)

        # movimentações aleatórias
        animals = list(Animal.objects.all())
        for _ in range(10):
            a = random.choice(animals)
            fr = a.group
            to = g1 if fr == g2 else g2
            Movement.objects.create(animal=a, from_group=fr, to_group=to, date=timezone.localdate() - timedelta(days=random.randint(1, 120)),
                                   reason=random.choice(["Rotação de pasto", "Engorda", "Separação", "Sanidade"]))

        # custos no mês
        today = timezone.localdate()
        for _ in range(18):
            CostEntry.objects.create(
                farm=farm,
                date=today - timedelta(days=random.randint(0, 28)),
                category=random.choice([c[0] for c in CostEntry.Category.choices]),
                description=random.choice(["Ração", "Suplemento mineral", "Vacina lote", "Medicamento", "Frete", "Funcionário"]),
                amount_brl=Decimal(random.randint(150, 2500))
            )

        self.stdout.write(self.style.SUCCESS("Dados demo criados/atualizados."))
