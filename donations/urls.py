from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.donation_list, name='list'),
    path('new/', views.donation_create, name='create'),
    path('<int:pk>/', views.donation_detail, name='detail'),
] 