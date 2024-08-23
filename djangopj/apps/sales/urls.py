from django.urls import path
from . import views


urlpatterns = [
    path("add_item/", views.add_item_to_list, name="add_item_to_list"),
    path("checkout/", views.proceed_to_checkout, name="checkout"),   
    path('delete_item/', views.delete_item_from_list, name='delete_item'),
    path('finish_checkout/', views.proceed_to_checkout, name="finish_checkout")
]
