from django.urls import path
from . import views

urlpatterns = [
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('add-to-order/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update/<int:item_id>/<str:action>/', views.cart_update, name='cart_update'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    
    path('', views.shop_view, name='catalog_shop'),
]


