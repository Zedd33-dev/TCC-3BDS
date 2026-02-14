# GadoManager (TCC) v2 — Gestão de Gado (Django + SQLite)

Melhorias extras (além do CRUD básico):
- **Dashboard** com mais indicadores e gráfico de peso médio por lote
- **Movimentação atualiza o lote do animal automaticamente**
- **Tratamentos/Sanidade** (medicação / vermífugo / etc.) com próxima dose
- **Custos/Financeiro** (ração, vacina, medicamento, mão de obra, outros) + total mensal
- **Central de Lembretes** (vacinas + tratamentos a vencer em 30 dias)
- **Exportação CSV** e **Relatórios em PDF** (Animais e Lembretes)

## Rodar
```bat
cd gado_tcc_site
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Login demo: **demo / demo12345**
