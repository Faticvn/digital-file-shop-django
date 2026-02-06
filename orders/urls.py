from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:file_id>/', views.cart_add, name='cart_add'),
    path('checkout/', views.checkout, name='checkout'),
]