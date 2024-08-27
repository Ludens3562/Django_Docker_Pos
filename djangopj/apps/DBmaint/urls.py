from django.urls import path
from . import views
from django.http import HttpResponse

urlpatterns = [
    path('filter_products/', views.filter_products, name='filter_products'),
    path('admin/transactions/<str:sale_id>/receipt/', views.generate_receipt_view, name='generate_receipt_view'),
]
