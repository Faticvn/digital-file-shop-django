from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    path('', views.file_list, name='list'),
    path('files/<int:pk>/', views.file_detail, name='detail'),
    path('seller/files/create/', views.file_create, name='create'),
]