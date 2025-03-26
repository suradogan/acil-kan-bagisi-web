from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import BloodDonation
from .forms import BloodDonationForm
from .serializers import BloodDonationSerializer
from hospitals.models import Hospital

# Create your views here.

@login_required
def donation_list(request):
    if request.user.is_hospital:
        donations = BloodDonation.objects.filter(hospital__id=request.user.id)
    else:
        donations = BloodDonation.objects.filter(donor=request.user)
    
    return render(request, 'donations/donation_list.html', {'donations': donations})

@login_required
def donation_create(request):
    if request.method == 'POST':
        form = BloodDonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.status = 'pending'
            donation.save()
            messages.success(request, "Kan bağışı başarıyla kaydedildi!")
            return redirect('donations:list')
    else:
        form = BloodDonationForm(initial={'blood_type': request.user.blood_type})
    
    hospitals = Hospital.objects.all()
    return render(request, 'donations/donation_form.html', {
        'form': form,
        'hospitals': hospitals
    })

@login_required
def donation_detail(request, pk):
    donation = get_object_or_404(BloodDonation, pk=pk)
    if request.user != donation.donor and not request.user.is_hospital:
        messages.error(request, "Bu işlem için yetkiniz yok!")
        return redirect('donations:list')
    
    return render(request, 'donations/donation_detail.html', {'donation': donation})

class BloodDonationViewSet(viewsets.ModelViewSet):
    queryset = BloodDonation.objects.all()
    serializer_class = BloodDonationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return BloodDonation.objects.all()
        elif user.is_hospital:
            return BloodDonation.objects.filter(hospital__user=user)
        else:
            return BloodDonation.objects.filter(donor=user)
    
    @action(detail=False, methods=['GET'])
    def my_donations(self, request):
        donations = BloodDonation.objects.filter(donor=request.user)
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def pending(self, request):
        donations = BloodDonation.objects.filter(status='pending')
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)
