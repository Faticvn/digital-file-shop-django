from django.urls import path
from . import views

app_name = "discounts"

urlpatterns = [
    path("create/", views.discount_create, name="create"),
]