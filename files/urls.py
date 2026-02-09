from django.urls import path
from . import views

app_name = "files"

urlpatterns = [
    path("", views.file_list, name="file_list"),
    path("create/", views.file_create, name="file_create"),
    path("<int:pk>/", views.file_detail, name="file_detail"),
]