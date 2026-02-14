from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),

    path('farms/', views.farm_list, name='farm_list'),
    path('farms/new/', views.farm_create, name='farm_create'),
    path('farms/<int:pk>/edit/', views.farm_edit, name='farm_edit'),
    path('farms/<int:pk>/delete/', views.farm_delete, name='farm_delete'),

    path('pastures/', views.pasture_list, name='pasture_list'),
    path('pastures/new/', views.pasture_create, name='pasture_create'),
    path('pastures/<int:pk>/edit/', views.pasture_edit, name='pasture_edit'),
    path('pastures/<int:pk>/delete/', views.pasture_delete, name='pasture_delete'),

    path('groups/', views.group_list, name='group_list'),
    path('groups/new/', views.group_create, name='group_create'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),

    path('animals/', views.animal_list, name='animal_list'),
    path('animals/new/', views.animal_create, name='animal_create'),
    path('animals/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('animals/<int:pk>/edit/', views.animal_edit, name='animal_edit'),
    path('animals/<int:pk>/delete/', views.animal_delete, name='animal_delete'),
    path('animals/export/', views.animals_export_csv, name='animals_export_csv'),
    path('animals/pdf/', views.animals_export_pdf, name='animals_export_pdf'),

    path('weights/', views.weight_list, name='weight_list'),
    path('weights/new/', views.weight_create, name='weight_create'),
    path('weights/<int:pk>/edit/', views.weight_edit, name='weight_edit'),
    path('weights/<int:pk>/delete/', views.weight_delete, name='weight_delete'),

    path('vaccinations/', views.vaccination_list, name='vaccination_list'),
    path('vaccinations/new/', views.vaccination_create, name='vaccination_create'),
    path('vaccinations/<int:pk>/edit/', views.vaccination_edit, name='vaccination_edit'),
    path('vaccinations/<int:pk>/delete/', views.vaccination_delete, name='vaccination_delete'),

    path('treatments/', views.treatment_list, name='treatment_list'),
    path('treatments/new/', views.treatment_create, name='treatment_create'),
    path('treatments/<int:pk>/edit/', views.treatment_edit, name='treatment_edit'),
    path('treatments/<int:pk>/delete/', views.treatment_delete, name='treatment_delete'),

    path('reminders/', views.reminders, name='reminders'),
    path('reminders/export/csv/', views.reminders_export_csv, name='reminders_export_csv'),
    path('reminders/export/pdf/', views.reminders_export_pdf, name='reminders_export_pdf'),

    path('movements/', views.movement_list, name='movement_list'),
    path('movements/new/', views.movement_create, name='movement_create'),
    path('movements/<int:pk>/edit/', views.movement_edit, name='movement_edit'),
    path('movements/<int:pk>/delete/', views.movement_delete, name='movement_delete'),

    path('sales/', views.sale_list, name='sale_list'),
    path('sales/new/', views.sale_create, name='sale_create'),
    path('sales/<int:pk>/edit/', views.sale_edit, name='sale_edit'),
    path('sales/<int:pk>/delete/', views.sale_delete, name='sale_delete'),

    path('costs/', views.cost_list, name='cost_list'),
    path('costs/new/', views.cost_create, name='cost_create'),
    path('costs/<int:pk>/edit/', views.cost_edit, name='cost_edit'),
    path('costs/<int:pk>/delete/', views.cost_delete, name='cost_delete'),
]
