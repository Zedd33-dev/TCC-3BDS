import django_filters
from django import forms
from django.db.models import Q
from .models import Farm, Pasture, HerdGroup, Animal, WeightRecord, Vaccination, Treatment, Movement, Sale, CostEntry


class BootstrapModelForm(forms.ModelForm):
    """Aplica classes do Bootstrap nos widgets automaticamente."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            widget = field.widget
            if getattr(widget, 'input_type', None) == 'hidden':
                continue
            css = widget.attrs.get('class', '')
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                base = 'form-select'
            elif isinstance(widget, (forms.CheckboxInput,)):
                base = 'form-check-input'
            else:
                base = 'form-control'
            widget.attrs['class'] = (css + ' ' + base).strip()
            if not widget.attrs.get('placeholder') and field.label:
                widget.attrs['placeholder'] = field.label


class FarmForm(BootstrapModelForm):
    class Meta:
        model = Farm
        fields = ['name', 'owner_name', 'city', 'state']
        labels = {
            'name': 'Nome',
            'owner_name': 'Dono/Responsável',
            'city': 'Cidade',
            'state': 'UF',
        }


class PastureForm(BootstrapModelForm):
    class Meta:
        model = Pasture
        fields = ['farm', 'name', 'area_ha', 'notes']
        labels = {
            'farm': 'Fazenda',
            'name': 'Nome',
            'area_ha': 'Área (ha)',
            'notes': 'Observações',
        }


class HerdGroupForm(BootstrapModelForm):
    class Meta:
        model = HerdGroup
        fields = ['farm', 'name', 'pasture', 'notes']
        labels = {
            'farm': 'Fazenda',
            'name': 'Nome do lote',
            'pasture': 'Pasto',
            'notes': 'Observações',
        }


class AnimalForm(BootstrapModelForm):
    class Meta:
        model = Animal
        fields = ['farm', 'group', 'ear_tag', 'name', 'breed', 'sex', 'birth_date', 'purchase_date', 'status', 'notes']
        labels = {
            'farm': 'Fazenda',
            'group': 'Lote',
            'ear_tag': 'Brinco/ID',
            'name': 'Nome',
            'breed': 'Raça',
            'sex': 'Sexo',
            'birth_date': 'Nascimento',
            'purchase_date': 'Entrada/Compra',
            'status': 'Status',
            'notes': 'Observações',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        birth_date = cleaned.get('birth_date')
        purchase_date = cleaned.get('purchase_date')
        if birth_date and purchase_date and purchase_date < birth_date:
            self.add_error('purchase_date', 'A data de entrada/compra não pode ser anterior ao nascimento.')
        return cleaned


class WeightForm(BootstrapModelForm):
    class Meta:
        model = WeightRecord
        fields = ['animal', 'date', 'weight_kg', 'notes']
        labels = {
            'animal': 'Animal',
            'date': 'Data',
            'weight_kg': 'Peso (kg)',
            'notes': 'Observações',
        }
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def clean_weight_kg(self):
        value = self.cleaned_data['weight_kg']
        if value <= 0:
            raise forms.ValidationError('O peso deve ser maior que zero.')
        return value


class VaccinationForm(BootstrapModelForm):
    class Meta:
        model = Vaccination
        fields = ['animal', 'vaccine', 'dose', 'date', 'next_due', 'veterinarian', 'notes']
        labels = {
            'animal': 'Animal',
            'vaccine': 'Vacina',
            'dose': 'Dose',
            'date': 'Data',
            'next_due': 'Próxima dose',
            'veterinarian': 'Veterinário',
            'notes': 'Observações',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'next_due': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('date')
        next_due = cleaned.get('next_due')
        if date and next_due and next_due < date:
            self.add_error('next_due', 'A próxima dose deve ser igual ou posterior à data da aplicação.')
        return cleaned


class TreatmentForm(BootstrapModelForm):
    class Meta:
        model = Treatment
        fields = ['animal', 'kind', 'product', 'date', 'next_due', 'notes']
        labels = {
            'animal': 'Animal',
            'kind': 'Tipo',
            'product': 'Produto',
            'date': 'Data',
            'next_due': 'Próximo',
            'notes': 'Observações',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'next_due': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('date')
        next_due = cleaned.get('next_due')
        if date and next_due and next_due < date:
            self.add_error('next_due', 'A próxima dose/data deve ser igual ou posterior à data do tratamento.')
        return cleaned


class MovementForm(BootstrapModelForm):
    class Meta:
        model = Movement
        fields = ['animal', 'from_group', 'to_group', 'date', 'reason']
        labels = {
            'animal': 'Animal',
            'from_group': 'De (lote)',
            'to_group': 'Para (lote)',
            'date': 'Data',
            'reason': 'Motivo',
        }
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def clean(self):
        cleaned = super().clean()
        from_group = cleaned.get('from_group')
        to_group = cleaned.get('to_group')
        animal = cleaned.get('animal')

        if from_group and to_group and from_group == to_group:
            self.add_error('to_group', 'O lote de destino deve ser diferente do lote de origem.')

        if animal and to_group and animal.farm_id != to_group.farm_id:
            self.add_error('to_group', 'O lote de destino precisa ser da mesma fazenda do animal.')

        if animal and from_group and animal.farm_id != from_group.farm_id:
            self.add_error('from_group', 'O lote de origem precisa ser da mesma fazenda do animal.')

        return cleaned


class SaleForm(BootstrapModelForm):
    class Meta:
        model = Sale
        fields = ['animal', 'date', 'buyer', 'price_brl', 'notes']
        labels = {
            'animal': 'Animal',
            'date': 'Data',
            'buyer': 'Comprador',
            'price_brl': 'Valor (R$)',
            'notes': 'Observações',
        }
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def clean_price_brl(self):
        value = self.cleaned_data['price_brl']
        if value <= 0:
            raise forms.ValidationError('O valor de venda deve ser maior que zero.')
        return value


class CostForm(BootstrapModelForm):
    class Meta:
        model = CostEntry
        fields = ['farm', 'date', 'category', 'description', 'amount_brl']
        labels = {
            'farm': 'Fazenda',
            'date': 'Data',
            'category': 'Categoria',
            'description': 'Descrição',
            'amount_brl': 'Valor (R$)',
        }
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def clean_amount_brl(self):
        value = self.cleaned_data['amount_brl']
        if value <= 0:
            raise forms.ValidationError('O valor do custo deve ser maior que zero.')
        return value


class AnimalFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q', label='Busca')

    class Meta:
        model = Animal
        fields = ['farm', 'group', 'sex', 'status']

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(ear_tag__icontains=value) |
            Q(name__icontains=value) |
            Q(breed__icontains=value)
        )
