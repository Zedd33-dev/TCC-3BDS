# Generated manually for demo (v2)
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Farm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('owner_name', models.CharField(blank=True, max_length=120)),
                ('city', models.CharField(blank=True, max_length=120)),
                ('state', models.CharField(blank=True, max_length=2)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pasture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('area_ha', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('notes', models.TextField(blank=True)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pastures', to='core.farm')),
            ],
        ),
        migrations.CreateModel(
            name='HerdGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('notes', models.TextField(blank=True)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='core.farm')),
                ('pasture', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.pasture')),
            ],
        ),
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ear_tag', models.CharField(max_length=40, unique=True)),
                ('name', models.CharField(blank=True, max_length=120)),
                ('breed', models.CharField(blank=True, max_length=120)),
                ('sex', models.CharField(choices=[('M', 'Macho'), ('F', 'Fêmea')], max_length=1)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('purchase_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('ATIVO', 'Ativo'), ('VENDIDO', 'Vendido'), ('MORTO', 'Morto'), ('PERDIDO', 'Perdido')], default='ATIVO', max_length=10)),
                ('notes', models.TextField(blank=True)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='animals', to='core.farm')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='animals', to='core.herdgroup')),
            ],
        ),
        migrations.CreateModel(
            name='WeightRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('weight_kg', models.DecimalField(decimal_places=2, max_digits=6)),
                ('notes', models.TextField(blank=True)),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weights', to='core.animal')),
            ],
            options={'ordering': ['-date']},
        ),
        migrations.CreateModel(
            name='Vaccination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vaccine', models.CharField(max_length=120)),
                ('dose', models.CharField(blank=True, max_length=60)),
                ('date', models.DateField()),
                ('next_due', models.DateField(blank=True, null=True)),
                ('veterinarian', models.CharField(blank=True, max_length=120)),
                ('notes', models.TextField(blank=True)),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vaccinations', to='core.animal')),
            ],
            options={'ordering': ['-date']},
        ),
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(max_length=120)),
                ('product', models.CharField(blank=True, max_length=120)),
                ('date', models.DateField()),
                ('next_due', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='treatments', to='core.animal')),
            ],
            options={'ordering': ['-date']},
        ),
        migrations.CreateModel(
            name='Movement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('reason', models.CharField(blank=True, max_length=200)),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movements', to='core.animal')),
                ('from_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moves_from', to='core.herdgroup')),
                ('to_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moves_to', to='core.herdgroup')),
            ],
            options={'ordering': ['-date']},
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('buyer', models.CharField(max_length=160)),
                ('price_brl', models.DecimalField(decimal_places=2, max_digits=10)),
                ('notes', models.TextField(blank=True)),
                ('animal', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sale', to='core.animal')),
            ],
        ),
        migrations.CreateModel(
            name='CostEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('category', models.CharField(choices=[('RACAO', 'Ração'), ('VACINA', 'Vacina'), ('MEDICAMENTO', 'Medicamento'), ('MAO_DE_OBRA', 'Mão de obra'), ('OUTROS', 'Outros')], max_length=20)),
                ('description', models.CharField(max_length=200)),
                ('amount_brl', models.DecimalField(decimal_places=2, max_digits=12)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='costs', to='core.farm')),
            ],
            options={'ordering': ['-date']},
        ),
    ]
