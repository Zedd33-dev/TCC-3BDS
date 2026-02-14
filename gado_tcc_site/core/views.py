import csv
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Farm, Pasture, HerdGroup, Animal, WeightRecord, Vaccination, Treatment, Movement, Sale, CostEntry
from .forms import (FarmForm, PastureForm, HerdGroupForm, AnimalForm,
                    WeightForm, VaccinationForm, TreatmentForm, MovementForm, SaleForm, CostForm, AnimalFilter)
from .pdf import simple_table_pdf

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    today = timezone.localdate()
    next_30 = today + timedelta(days=30)
    threshold_no_weight = today - timedelta(days=60)

    total_animals = Animal.objects.count()
    active_animals = Animal.objects.filter(status=Animal.Status.ACTIVE).count()
    sold_animals = Animal.objects.filter(status=Animal.Status.SOLD).count()
    farms = Farm.objects.count()
    groups = HerdGroup.objects.count()

    overdue_vacc = Vaccination.objects.filter(next_due__isnull=False, next_due__lt=today).count()
    overdue_trt = Treatment.objects.filter(next_due__isnull=False, next_due__lt=today).count()
    due_vacc = Vaccination.objects.filter(next_due__isnull=False, next_due__gte=today, next_due__lte=next_30).count()
    due_trt = Treatment.objects.filter(next_due__isnull=False, next_due__gte=today, next_due__lte=next_30).count()

    # Custos do mês
    month_start = today.replace(day=1)
    month_cost = CostEntry.objects.filter(date__gte=month_start, date__lte=today).aggregate(total=Sum('amount_brl'))['total'] or Decimal('0.00')

    # status chart
    status_counts = list(Animal.objects.values('status').annotate(c=Count('id')))

    # último peso por animal
    latest_dates = WeightRecord.objects.values('animal').annotate(last=Max('date'))
    latest_pairs = {(x['animal'], x['last']) for x in latest_dates if x['last'] is not None}
    latest_by_animal = {}
    for aid, d in latest_pairs:
        wr = WeightRecord.objects.filter(animal_id=aid, date=d).only('weight_kg', 'animal_id').first()
        if wr:
            latest_by_animal[aid] = float(wr.weight_kg)

    # peso médio do rebanho (última pesagem)
    overall_avg_weight = None
    if latest_by_animal:
        overall_avg_weight = round(sum(latest_by_animal.values()) / len(latest_by_animal), 2)

    # animais sem pesagem há 60 dias (ou sem pesagem)
    animals_no_weight = Animal.objects.annotate(last_w=Max('weights__date')).filter(
        Q(last_w__isnull=True) | Q(last_w__lt=threshold_no_weight)
    ).count()

    # GMD médio (primeira vs última pesagem do animal)
    gmd_values = []
    for a in Animal.objects.all().only('id'):
        ws = list(WeightRecord.objects.filter(animal_id=a.id).order_by('date').values_list('date', 'weight_kg'))
        if len(ws) >= 2:
            d0, w0 = ws[0]
            d1, w1 = ws[-1]
            days = (d1 - d0).days
            if days > 0:
                gmd = (float(w1) - float(w0)) / days
                gmd_values.append(gmd)
    gmd_avg = round(sum(gmd_values) / len(gmd_values), 3) if gmd_values else None

    # agrega por group atual
    group_map = {g.id: {'name': g.name, 'sum': 0.0, 'n': 0} for g in HerdGroup.objects.all()}
    for a in Animal.objects.select_related('group').all().only('id', 'group_id'):
        if a.id in latest_by_animal and a.group_id in group_map:
            group_map[a.group_id]['sum'] += latest_by_animal[a.id]
            group_map[a.group_id]['n'] += 1

    group_labels = []
    group_avg = []
    for g in group_map.values():
        if g['n'] > 0:
            group_labels.append(g['name'])
            group_avg.append(round(g['sum']/g['n'], 2))

    return render(request, 'dashboard.html', {
        'total_animals': total_animals,
        'active_animals': active_animals,
        'sold_animals': sold_animals,
        'farms': farms,
        'groups': groups,
        'overdue_vacc': overdue_vacc,
        'overdue_trt': overdue_trt,
        'due_vacc': due_vacc,
        'due_trt': due_trt,
        'month_cost': month_cost,
        'status_counts': status_counts,
        'group_labels': group_labels,
        'group_avg': group_avg,
        'overall_avg_weight': overall_avg_weight,
        'gmd_avg': gmd_avg,
        'animals_no_weight': animals_no_weight,
        'title': 'Dashboard'
    })


# --- helpers ---
def _crud_list(request, template, qs, ctx=None):
    ctx = ctx or {}
    ctx['items'] = qs
    return render(request, template, ctx)

def _crud_form(request, template, form, success_url, title):
    if request.method == 'POST':
        form = form.__class__(request.POST, instance=form.instance)
        if form.is_valid():
            form.save()
            messages.success(request, f'{title} salvo com sucesso.')
            return redirect(success_url)
        messages.error(request, 'Corrija os campos do formulário.')
    return render(request, template, {'form': form, 'title': title})

def _crud_delete(request, obj, success_url, title):
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'{title} removido.')
        return redirect(success_url)
    return render(request, 'generic/confirm_delete.html', {'object': obj, 'title': title})

# Farms
@login_required
def farm_list(request):
    return _crud_list(request, 'farms/list.html', Farm.objects.all().order_by('name'), {'title': 'Fazendas'})

@login_required
def farm_create(request):
    return _crud_form(request, 'generic/form.html', FarmForm(), 'farm_list', 'Fazenda')

@login_required
def farm_edit(request, pk):
    return _crud_form(request, 'generic/form.html', FarmForm(instance=get_object_or_404(Farm, pk=pk)), 'farm_list', 'Fazenda')

@login_required
def farm_delete(request, pk):
    return _crud_delete(request, get_object_or_404(Farm, pk=pk), 'farm_list', 'Fazenda')

# Pastures
@login_required
def pasture_list(request):
    return _crud_list(request, 'pastures/list.html', Pasture.objects.select_related('farm').all(), {'title': 'Pastos/Piquetes'})

@login_required
def pasture_create(request):
    return _crud_form(request, 'generic/form.html', PastureForm(), 'pasture_list', 'Pasto/Piquete')

@login_required
def pasture_edit(request, pk):
    return _crud_form(request, 'generic/form.html', PastureForm(instance=get_object_or_404(Pasture, pk=pk)), 'pasture_list', 'Pasto/Piquete')

@login_required
def pasture_delete(request, pk):
    return _crud_delete(request, get_object_or_404(Pasture, pk=pk), 'pasture_list', 'Pasto/Piquete')

# Groups
@login_required
def group_list(request):
    return _crud_list(request, 'groups/list.html', HerdGroup.objects.select_related('farm','pasture').all(), {'title': 'Lotes'})

@login_required
def group_create(request):
    return _crud_form(request, 'generic/form.html', HerdGroupForm(), 'group_list', 'Lote')

@login_required
def group_edit(request, pk):
    return _crud_form(request, 'generic/form.html', HerdGroupForm(instance=get_object_or_404(HerdGroup, pk=pk)), 'group_list', 'Lote')

@login_required
def group_delete(request, pk):
    return _crud_delete(request, get_object_or_404(HerdGroup, pk=pk), 'group_list', 'Lote')

# Animals
@login_required
def animal_list(request):
    f = AnimalFilter(request.GET, queryset=Animal.objects.select_related('farm','group').all().order_by('ear_tag'))
    return render(request, 'animals/list.html', {'filter': f, 'items': f.qs, 'title': 'Animais'})

@login_required
def animal_detail(request, pk):
    obj = get_object_or_404(Animal.objects.select_related('farm','group'), pk=pk)
    weights = obj.weights.all()
    vaccs = obj.vaccinations.all()
    trts = obj.treatments.all()
    moves = obj.movements.select_related('from_group','to_group').all()
    sale = getattr(obj, 'sale', None)

    weights_list = list(weights.order_by('date'))
    labels = [w.date.strftime('%Y-%m-%d') for w in weights_list]
    data = [float(w.weight_kg) for w in weights_list]

    # KPIs (último peso + GMD)
    last_weight = data[-1] if data else None
    gmd = None
    recent_gmd = None
    if len(weights_list) >= 2:
        d0, w0 = weights_list[0].date, float(weights_list[0].weight_kg)
        d1, w1 = weights_list[-1].date, float(weights_list[-1].weight_kg)
        days = (d1 - d0).days
        if days > 0:
            gmd = (w1 - w0) / days

        # GMD recente (últimas 2 pesagens)
        d0r, w0r = weights_list[-2].date, float(weights_list[-2].weight_kg)
        d1r, w1r = weights_list[-1].date, float(weights_list[-1].weight_kg)
        daysr = (d1r - d0r).days
        if daysr > 0:
            recent_gmd = (w1r - w0r) / daysr

    # Linha do tempo (ordem decrescente por data)
    timeline = []
    for w in weights:
        timeline.append({
            'date': w.date,
            'type': 'Pesagem',
            'title': f"{w.weight_kg} kg",
            'detail': (w.notes or '').strip(),
            'badge': 'primary'
        })
    for v in vaccs:
        timeline.append({
            'date': v.date,
            'type': 'Vacina',
            'title': v.vaccine,
            'detail': f"Dose: {v.dose}" if v.dose else '',
            'badge': 'success'
        })
    for t in trts:
        name = f"{t.kind} {('- ' + t.product) if t.product else ''}".strip()
        timeline.append({
            'date': t.date,
            'type': 'Tratamento',
            'title': name,
            'detail': (t.notes or '').strip(),
            'badge': 'warning'
        })
    for mv in moves:
        frm = mv.from_group.name if mv.from_group else '—'
        to = mv.to_group.name if mv.to_group else '—'
        timeline.append({
            'date': mv.date,
            'type': 'Movimentação',
            'title': f"{frm} → {to}",
            'detail': (mv.reason or '').strip(),
            'badge': 'info'
        })
    if sale:
        timeline.append({
            'date': sale.date,
            'type': 'Venda',
            'title': f"R$ {sale.price_brl}",
            'detail': f"Comprador: {sale.buyer}",
            'badge': 'dark'
        })
    # nascimento/compra como eventos
    if obj.birth_date:
        timeline.append({'date': obj.birth_date, 'type': 'Cadastro', 'title': 'Nascimento', 'detail': '', 'badge': 'secondary'})
    if obj.purchase_date:
        timeline.append({'date': obj.purchase_date, 'type': 'Cadastro', 'title': 'Entrada/Compra', 'detail': '', 'badge': 'secondary'})

    timeline.sort(key=lambda x: x['date'] or timezone.localdate(), reverse=True)

    return render(request, 'animals/detail.html', {
        'object': obj, 'weights': weights, 'vaccs': vaccs, 'trts': trts,
        'moves': moves, 'sale': sale,
        'chart_labels': labels, 'chart_data': data,
        'last_weight': last_weight,
        'gmd': gmd,
        'recent_gmd': recent_gmd,
        'timeline': timeline,
        'title': f'Animal {obj.ear_tag}'
    })

@login_required

def animal_create(request):
    return _crud_form(request, 'generic/form.html', AnimalForm(), 'animal_list', 'Animal')

@login_required
def animal_edit(request, pk):
    return _crud_form(request, 'generic/form.html', AnimalForm(instance=get_object_or_404(Animal, pk=pk)), 'animal_list', 'Animal')

@login_required
def animal_delete(request, pk):
    return _crud_delete(request, get_object_or_404(Animal, pk=pk), 'animal_list', 'Animal')

@login_required
def animals_export_csv(request):
    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename=animais.csv'
    wri = csv.writer(resp)
    wri.writerow(['Brinco', 'Nome', 'Fazenda', 'Lote', 'Raça', 'Sexo', 'Nascimento', 'Status'])
    for a in Animal.objects.select_related('farm', 'group').all().order_by('ear_tag'):
        wri.writerow([a.ear_tag, a.name, a.farm.name, a.group.name if a.group else '', a.breed, a.get_sex_display(), a.birth_date, a.get_status_display()])
    return resp

@login_required
def animals_export_pdf(request):
    rows = []
    for a in Animal.objects.select_related('farm','group').all().order_by('ear_tag'):
        rows.append([a.ear_tag, a.name or '', a.farm.name, (a.group.name if a.group else ''), a.get_status_display()])
    pdf = simple_table_pdf("Relatório — Animais", ["Brinco","Nome","Fazenda","Lote","Status"], rows)
    resp = HttpResponse(pdf, content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename=relatorio_animais.pdf'
    return resp

# Weights
@login_required
def weight_list(request):
    return _crud_list(request, 'weights/list.html', WeightRecord.objects.select_related('animal').all(), {'title': 'Pesagens'})

@login_required
def weight_create(request):
    return _crud_form(request, 'generic/form.html', WeightForm(), 'weight_list', 'Pesagem')

@login_required
def weight_edit(request, pk):
    return _crud_form(request, 'generic/form.html', WeightForm(instance=get_object_or_404(WeightRecord, pk=pk)), 'weight_list', 'Pesagem')

@login_required
def weight_delete(request, pk):
    return _crud_delete(request, get_object_or_404(WeightRecord, pk=pk), 'weight_list', 'Pesagem')

# Vaccinations
@login_required
def vaccination_list(request):
    return _crud_list(request, 'vaccinations/list.html', Vaccination.objects.select_related('animal').all(), {'title': 'Vacinas'})

@login_required
def vaccination_create(request):
    return _crud_form(request, 'generic/form.html', VaccinationForm(), 'vaccination_list', 'Vacina')

@login_required
def vaccination_edit(request, pk):
    return _crud_form(request, 'generic/form.html', VaccinationForm(instance=get_object_or_404(Vaccination, pk=pk)), 'vaccination_list', 'Vacina')

@login_required
def vaccination_delete(request, pk):
    return _crud_delete(request, get_object_or_404(Vaccination, pk=pk), 'vaccination_list', 'Vacina')

# Treatments
@login_required
def treatment_list(request):
    return _crud_list(request, 'treatments/list.html', Treatment.objects.select_related('animal').all(), {'title': 'Tratamentos'})

@login_required
def treatment_create(request):
    return _crud_form(request, 'generic/form.html', TreatmentForm(), 'treatment_list', 'Tratamento')

@login_required
def treatment_edit(request, pk):
    return _crud_form(request, 'generic/form.html', TreatmentForm(instance=get_object_or_404(Treatment, pk=pk)), 'treatment_list', 'Tratamento')

@login_required
def treatment_delete(request, pk):
    return _crud_delete(request, get_object_or_404(Treatment, pk=pk), 'treatment_list', 'Tratamento')

# Reminders (Vaccinations + Treatments)
@login_required
def reminders(request):
    today = timezone.localdate()
    limit = today + timedelta(days=30)
    vacc = Vaccination.objects.select_related('animal').filter(next_due__isnull=False, next_due__lte=limit)
    trt = Treatment.objects.select_related('animal').filter(next_due__isnull=False, next_due__lte=limit)

    items = []
    for v in vacc:
        items.append({
            'type': 'Vacina',
            'animal': str(v.animal),
            'name': v.vaccine,
            'due': v.next_due,
            'notes': v.dose or ''
        })
    for t in trt:
        items.append({
            'type': 'Tratamento',
            'animal': str(t.animal),
            'name': f"{t.kind} {('- ' + t.product) if t.product else ''}".strip(),
            'due': t.next_due,
            'notes': t.notes[:80] if t.notes else ''
        })
    items.sort(key=lambda x: x['due'] or today)
    return render(request, 'reminders/list.html', {'items': items, 'title': 'Lembretes (30 dias)'})

@login_required
def reminders_export_csv(request):
    today = timezone.localdate()
    limit = today + timedelta(days=30)
    vacc = Vaccination.objects.select_related('animal').filter(next_due__isnull=False, next_due__lte=limit)
    trt = Treatment.objects.select_related('animal').filter(next_due__isnull=False, next_due__lte=limit)

    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename=lembretes_30dias.csv'
    wri = csv.writer(resp)
    wri.writerow(['Tipo', 'Animal', 'Nome', 'Vencimento', 'Obs'])

    for v in vacc:
        wri.writerow(['Vacina', v.animal.ear_tag, v.vaccine, v.next_due, v.dose])
    for t in trt:
        wri.writerow(['Tratamento', t.animal.ear_tag, t.kind, t.next_due, t.product])
    return resp

@login_required
def reminders_export_pdf(request):
    today = timezone.localdate()
    limit = today + timedelta(days=30)
    rows = []
    for v in Vaccination.objects.select_related('animal').filter(next_due__isnull=False, next_due__lte=limit).order_by('next_due'):
        rows.append(['Vacina', v.animal.ear_tag, v.vaccine, str(v.next_due), v.dose or ''])
    for t in Treatment.objects.select_related('animal').filter(next_due__isnull=False, next_due__lte=limit).order_by('next_due'):
        rows.append(['Trat.', t.animal.ear_tag, t.kind, str(t.next_due), t.product or ''])
    pdf = simple_table_pdf("Relatório — Lembretes (30 dias)", ["Tipo","Animal","Nome","Venc.","Obs"], rows)
    resp = HttpResponse(pdf, content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename=relatorio_lembretes_30dias.pdf'
    return resp

# Movements
@login_required
def movement_list(request):
    return _crud_list(request, 'movements/list.html', Movement.objects.select_related('animal','from_group','to_group').all(), {'title': 'Movimentações'})

@login_required
def movement_create(request):
    return _crud_form(request, 'generic/form.html', MovementForm(), 'movement_list', 'Movimentação')

@login_required
def movement_edit(request, pk):
    return _crud_form(request, 'generic/form.html', MovementForm(instance=get_object_or_404(Movement, pk=pk)), 'movement_list', 'Movimentação')

@login_required
def movement_delete(request, pk):
    return _crud_delete(request, get_object_or_404(Movement, pk=pk), 'movement_list', 'Movimentação')

# Sales
@login_required
def sale_list(request):
    return _crud_list(request, 'sales/list.html', Sale.objects.select_related('animal').all(), {'title': 'Vendas/Baixas'})

@login_required
def sale_create(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save()
            sale.animal.status = Animal.Status.SOLD
            sale.animal.save(update_fields=['status'])
            messages.success(request, 'Venda salva e animal marcado como VENDIDO.')
            return redirect('sale_list')
        messages.error(request, 'Corrija os campos do formulário.')
        return render(request, 'generic/form.html', {'form': form, 'title': 'Venda'})
    return render(request, 'generic/form.html', {'form': SaleForm(), 'title': 'Venda'})

@login_required
def sale_edit(request, pk):
    return _crud_form(request, 'generic/form.html', SaleForm(instance=get_object_or_404(Sale, pk=pk)), 'sale_list', 'Venda')

@login_required
def sale_delete(request, pk):
    return _crud_delete(request, get_object_or_404(Sale, pk=pk), 'sale_list', 'Venda')

# Costs
@login_required
def cost_list(request):
    qs = CostEntry.objects.select_related('farm').all()
    today = timezone.localdate()
    month_start = today.replace(day=1)
    total_month = CostEntry.objects.filter(date__gte=month_start, date__lte=today).aggregate(total=Sum('amount_brl'))['total'] or Decimal('0.00')
    by_cat = list(CostEntry.objects.filter(date__gte=month_start, date__lte=today).values('category').annotate(total=Sum('amount_brl')).order_by('-total'))
    return render(request, 'costs/list.html', {'items': qs, 'title': 'Custos', 'total_month': total_month, 'by_cat': by_cat})

@login_required
def cost_create(request):
    return _crud_form(request, 'generic/form.html', CostForm(), 'cost_list', 'Custo')

@login_required
def cost_edit(request, pk):
    return _crud_form(request, 'generic/form.html', CostForm(instance=get_object_or_404(CostEntry, pk=pk)), 'cost_list', 'Custo')

@login_required
def cost_delete(request, pk):
    return _crud_delete(request, get_object_or_404(CostEntry, pk=pk), 'cost_list', 'Custo')
