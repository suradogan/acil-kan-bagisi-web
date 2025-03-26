from django.urls import path
from . import views

app_name = 'hospitals'

urlpatterns = [
    path('', views.hospital_list, name='list'),
    path('<int:pk>/', views.hospital_detail, name='detail'),
    path('dashboard/', views.hospital_dashboard, name='dashboard'),
] 