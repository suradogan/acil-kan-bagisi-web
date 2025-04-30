from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import BloodDonation, EmergencyBloodRequest, BloodDonationResponse
from .forms import BloodDonationForm
from .serializers import (
    BloodDonationSerializer, 
    EmergencyBloodRequestSerializer,
    BloodDonationResponseSerializer
)
from hospitals.models import Hospital
from users.models import User
import math

# Create your views here.

@login_required
def donation_list(request):
    if request.user.is_hospital:
        # Hastane ise kendi hastanesine yapılan bağışları göster
        donations = BloodDonation.objects.filter(hospital=request.user).order_by('-donation_date')
    else:
        # Normal kullanıcı ise kendi bağışlarını göster
        donations = BloodDonation.objects.filter(donor=request.user).order_by('-donation_date')
    
    context = {
        'donations': donations,
        'can_donate': request.user.can_donate(),
        'days_until_next_donation': request.user.days_until_next_donation(),
    }
    
    return render(request, 'donations/donation_list.html', context)

@login_required
def create_donation(request):
    if request.method == 'POST':
        form = BloodDonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.blood_type = request.user.blood_type
            donation.save()
            
            # Kullanıcının son bağış tarihini güncelle
            request.user.last_donation_date = donation.donation_date.date()
            request.user.save(update_fields=['last_donation_date'])
            
            messages.success(request, "Bağış kaydınız oluşturuldu!")
            return redirect('donations:list')
    else:
        form = BloodDonationForm()
    
    context = {
        'form': form,
        'hospitals': Hospital.objects.all(),
    }
    
    return render(request, 'donations/create_donation.html', context)

@login_required
def emergency_requests(request):
    # Aktif acil talepleri listele
    requests = EmergencyBloodRequest.objects.filter(
        status='active',
        expires_at__gt=timezone.now()
    )
    
    # Kullanıcı bir hastane ise, kendi taleplerini göster
    if request.user.is_hospital:
        requests = requests.filter(hospital=request.user)
    
    context = {
        'emergency_requests': requests,
    }
    
    return render(request, 'donations/emergency_requests.html', context)

class BloodDonationViewSet(viewsets.ModelViewSet):
    queryset = BloodDonation.objects.all()
    serializer_class = BloodDonationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff:
            return BloodDonation.objects.all()
        
        if user.is_hospital:
            return BloodDonation.objects.filter(hospital__id=user.id)
            
        return BloodDonation.objects.filter(donor=user)
    
    def perform_create(self, serializer):
        serializer.save(donor=self.request.user)
        
        # Kullanıcının son bağış tarihini güncelle
        user = self.request.user
        user.last_donation_date = timezone.now().date()
        user.save(update_fields=['last_donation_date'])
        
    @action(detail=False, methods=['get'])
    def my_donations(self, request):
        donations = BloodDonation.objects.filter(donor=request.user).order_by('-donation_date')
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

class EmergencyBloodRequestViewSet(viewsets.ModelViewSet):
    queryset = EmergencyBloodRequest.objects.all()
    serializer_class = EmergencyBloodRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Aktif acil talepler için filtreleme
        queryset = EmergencyBloodRequest.objects.filter(
            status='active',
            expires_at__gt=timezone.now()
        )
        
        # Kan grubu filtreleme
        blood_type = self.request.query_params.get('blood_type', None)
        if blood_type:
            queryset = queryset.filter(blood_type=blood_type)
            
        # Hastane filtreleme
        hospital_id = self.request.query_params.get('hospital', None)
        if hospital_id:
            queryset = queryset.filter(hospital__id=hospital_id)
            
        # Aciliyet seviyesi filtreleme
        urgency = self.request.query_params.get('urgency', None)
        if urgency:
            queryset = queryset.filter(urgency_level=urgency)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)
        
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        requests = EmergencyBloodRequest.objects.filter(requester=request.user).order_by('-created_at')
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Kullanıcının konumuna yakın acil kan ihtiyaçlarını listele"""
        user = request.user
        
        # Kullanıcının konum bilgisi yoksa hata döndür
        if not user.latitude or not user.longitude:
            return Response(
                {"error": "Konum bilginiz bulunmamaktadır. Lütfen profilinizi güncelleyin."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Mesafe filtreleme (km cinsinden)
        distance = float(request.query_params.get('distance', 10.0))
        
        # Aktif acil talepler
        active_requests = EmergencyBloodRequest.objects.filter(
            status='active',
            expires_at__gt=timezone.now()
        )
        
        # Kan grubu uyumluluğu kontrolü (basitleştirilmiş)
        if user.blood_type:
            compatible_requests = []
            for req in active_requests:
                # Basit uyumluluk kontrolü
                if is_blood_compatible(user.blood_type, req.blood_type):
                    # Mesafe hesaplama (basit Haversine formülü)
                    hospital = req.hospital
                    if hospital.latitude and hospital.longitude:
                        dist = calculate_distance(
                            user.latitude, user.longitude,
                            hospital.latitude, hospital.longitude
                        )
                        if dist <= distance:
                            req.distance = dist  # Mesafe bilgisini ekle
                            compatible_requests.append(req)
            
            # Mesafeye göre sırala
            compatible_requests.sort(key=lambda x: x.distance)
            serializer = self.get_serializer(compatible_requests, many=True)
            return Response(serializer.data)
        
        return Response([])

class BloodDonationResponseViewSet(viewsets.ModelViewSet):
    queryset = BloodDonationResponse.objects.all()
    serializer_class = BloodDonationResponseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff:
            return BloodDonationResponse.objects.all()
            
        if user.is_hospital:
            # Hastane kendi acil taleplerine gelen yanıtları görebilir
            hospital_requests = EmergencyBloodRequest.objects.filter(hospital=user)
            return BloodDonationResponse.objects.filter(emergency_request__in=hospital_requests)
            
        # Normal kullanıcı kendi yanıtlarını görebilir
        return BloodDonationResponse.objects.filter(donor=user)
    
    def perform_create(self, serializer):
        # Aynı talebe birden fazla yanıt vermeyi engelle
        emergency_request = get_object_or_404(
            EmergencyBloodRequest, 
            pk=self.request.data.get('emergency_request')
        )
        
        # Zaten yanıt verilmiş mi kontrol et
        if BloodDonationResponse.objects.filter(
            emergency_request=emergency_request,
            donor=self.request.user
        ).exists():
            raise PermissionDenied("Bu talebe zaten yanıt verdiniz.")
            
        # Talep hala aktif mi kontrol et
        if emergency_request.status != 'active' or emergency_request.is_expired():
            raise PermissionDenied("Bu talep artık aktif değil.")
            
        serializer.save(donor=self.request.user)
        
    @action(detail=False, methods=['get'])
    def my_responses(self, request):
        responses = BloodDonationResponse.objects.filter(donor=request.user).order_by('-created_at')
        serializer = self.get_serializer(responses, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Hastane, bağışçının yanıtını kabul eder"""
        response = self.get_object()
        
        # Sadece hastane kabul edebilir
        if not request.user.is_hospital:
            raise PermissionDenied("Bu işlemi gerçekleştirme yetkiniz yok.")
            
        # Yanıtın ait olduğu acil talep bu hastaneye ait mi kontrol et
        if response.emergency_request.hospital.id != request.user.id:
            raise PermissionDenied("Bu yanıt sizin hastanenizin talebiyle ilgili değil.")
            
        # Yanıt hala beklemede mi kontrol et
        if response.status != 'pending':
            return Response(
                {"error": "Bu yanıt zaten işlenmiş."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        response.status = 'accepted'
        response.save()
        
        return Response({"status": "accepted"})

# Yardımcı fonksiyonlar

def is_blood_compatible(donor_type, recipient_type):
    """
    Basitleştirilmiş kan uyumluluğu kontrolü
    """
    # Kan bağışı uyumluluk tablosu
    compatibility = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+']
    }
    
    if donor_type in compatibility:
        return recipient_type in compatibility[donor_type]
    return False

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Haversine formülü ile iki nokta arasındaki mesafeyi hesaplar (km cinsinden)
    """
    # Dünya yarıçapı (km)
    R = 6371.0
    
    # Derece cinsinden değerleri radyan cinsine çevir
    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))
    
    # Haversine formülü
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance
