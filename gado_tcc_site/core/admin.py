from django.contrib import admin
from .models import Farm, Pasture, HerdGroup, Animal, WeightRecord, Vaccination, Treatment, Movement, Sale, CostEntry

admin.site.register(Farm)
admin.site.register(Pasture)
admin.site.register(HerdGroup)
admin.site.register(Animal)
admin.site.register(WeightRecord)
admin.site.register(Vaccination)
admin.site.register(Treatment)
admin.site.register(Movement)
admin.site.register(Sale)
admin.site.register(CostEntry)
