from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework import viewsets, permissions
from .models import Hospital
from .serializers import HospitalSerializer
from donations.models import BloodDonation

# Create your views here.

def hospital_list(request):
    hospitals = Hospital.objects.all()
    return render(request, 'hospitals/hospital_list.html', {'hospitals': hospitals})

def hospital_detail(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    return render(request, 'hospitals/hospital_detail.html', {'hospital': hospital})

def is_hospital(user):
    return user.is_hospital

@login_required
@user_passes_test(is_hospital)
def hospital_dashboard(request):
    donations = BloodDonation.objects.filter(hospital__id=request.user.id)
    pending_donations = donations.filter(status='pending').count()
    completed_donations = donations.filter(status='completed').count()
    
    # Kan grubu dağılımı
    blood_groups = {}
    for donation in donations:
        if donation.blood_type in blood_groups:
            blood_groups[donation.blood_type] += 1
        else:
            blood_groups[donation.blood_type] = 1
    
    context = {
        'total_donations': donations.count(),
        'pending_donations': pending_donations,
        'completed_donations': completed_donations,
        'blood_groups': blood_groups,
        'recent_donations': donations.order_by('-created_at')[:5]
    }
    
    return render(request, 'hospitals/dashboard.html', context)

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]
