from django.urls import path
from . import views

urlpatterns = [
    path('filter_products/', views.filter_products, name='filter_products'),
]
