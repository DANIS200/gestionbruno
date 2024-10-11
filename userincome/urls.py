from django.urls import path
from . import views

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="income"),
    path('add-income', views.add_income, name="add-income"),
    path('edit-income/<int:id>', views.income_edit, name="income-edit"),
    path('income-delete/<int:id>', views.delete_income, name="income-delete"),
    path('search-income', csrf_exempt(views.search_income),
         name="search_income"),
    path('stats', views.stats_view,
         name="stat"),
    
    path('export_csv', views.export_csv,
         name="expor-csv"),
    path('export_excel', views.export_excel,
        name="expor-excel"),
    path('export_pdf', views.export_pdf,
         name="expor-pdf"),
    path('summary_by_source/', views.summary_by_source, name='summary_by_source'),
]
