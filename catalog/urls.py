from django.urls import path
from . import views

urlpatterns = [
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('add-to-order/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
]
