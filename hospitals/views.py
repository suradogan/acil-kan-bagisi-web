from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Hospital
from .serializers import HospitalSerializer
from donations.models import BloodDonation, EmergencyBloodRequest

# Create your views here.

@login_required
def hospital_list(request):
    hospitals = Hospital.objects.all()
    return render(request, 'hospitals/hospital_list.html', {'hospitals': hospitals})

@login_required
def hospital_detail(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    donations = BloodDonation.objects.filter(hospital=hospital)
    
    context = {
        'hospital': hospital,
        'donations': donations,
    }
    
    return render(request, 'hospitals/hospital_detail.html', context)

@login_required
def hospital_map(request):
    hospitals = Hospital.objects.all()
    
    # Şehir listesi oluştur (filtreleme için)
    cities = Hospital.objects.values_list('city', flat=True).distinct().order_by('city')
    
    context = {
        'hospitals': hospitals,
        'cities': cities,
    }
    
    return render(request, 'hospitals/map.html', context)

def is_hospital(user):
    return user.is_hospital

@login_required
@user_passes_test(is_hospital)
def hospital_dashboard(request):
    # Sadece hastane kullanıcıları erişebilir
    if not request.user.is_hospital:
        return redirect('core:home')
        
    hospital = request.user
    
    # İstatistikleri topla
    total_donations = BloodDonation.objects.filter(hospital=hospital).count()
    pending_donations = BloodDonation.objects.filter(hospital=hospital, status='pending').count()
    completed_donations = BloodDonation.objects.filter(hospital=hospital, status='completed').count()
    
    # Aktif acil kan talepleri
    active_requests = EmergencyBloodRequest.objects.filter(
        hospital=hospital,
        status='active'
    ).count()
    
    # Kan tiplerine göre bağışlar
    blood_type_data = BloodDonation.objects.filter(hospital=hospital).values('blood_type').annotate(
        count=Count('id')
    ).order_by('blood_type')
    
    context = {
        'hospital': hospital,
        'total_donations': total_donations,
        'pending_donations': pending_donations,
        'completed_donations': completed_donations,
        'active_requests': active_requests,
        'blood_type_data': blood_type_data,
    }
    
    return render(request, 'hospitals/dashboard.html', context)

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def donations(self, request, pk=None):
        hospital = self.get_object()
        donations = BloodDonation.objects.filter(hospital=hospital)
        
        from donations.serializers import BloodDonationSerializer
        serializer = BloodDonationSerializer(donations, many=True)
        
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def emergency_requests(self, request, pk=None):
        hospital = self.get_object()
        requests = EmergencyBloodRequest.objects.filter(hospital=hospital)
        
        from donations.serializers import EmergencyBloodRequestSerializer
        serializer = EmergencyBloodRequestSerializer(requests, many=True)
        
        return Response(serializer.data)
