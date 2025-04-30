from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.donation_list, name='list'),
    path('create/', views.create_donation, name='create'),
    path('emergency/', views.emergency_requests, name='emergency'),
] 