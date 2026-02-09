from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:file_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:file_id>/", views.cart_remove, name="cart_remove"),

    path("checkout/", views.checkout, name="checkout"),
    path("downloads/", views.my_downloads, name="my_downloads"),
    path("download/<int:file_id>/", views.download_file, name="download"),
]