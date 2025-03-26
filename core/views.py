from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User
from hospitals.models import Hospital
from donations.models import BloodDonation

def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    total_users = User.objects.filter(is_hospital=False).count()
    total_hospitals = Hospital.objects.count()
    total_donations = BloodDonation.objects.count()
    
    # Kan tiplerine göre bağış sayıları
    blood_types = {}
    for blood_type in User.BLOOD_TYPES:
        blood_types[blood_type[0]] = BloodDonation.objects.filter(blood_type=blood_type[0]).count()
    
    return Response({
        'total_users': total_users,
        'total_hospitals': total_hospitals,
        'total_donations': total_donations,
        'blood_types': blood_types
    })
