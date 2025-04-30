from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_protect
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .serializers import UserSerializer, UserProfileSerializer
from donations.models import BloodDonation
from rest_framework_simplejwt.tokens import RefreshToken

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create' or self.action == 'register':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'profile':
            return UserProfileSerializer
        return UserSerializer
        
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        user = request.user
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
            
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = request.user
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not old_password or not new_password or not confirm_password:
            return Response({'error': 'Tüm şifre alanları zorunludur'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not user.check_password(old_password):
            return Response({'error': 'Mevcut şifre yanlış'}, status=status.HTTP_400_BAD_REQUEST)
            
        if new_password != confirm_password:
            return Response({'error': 'Yeni şifreler eşleşmiyor'}, status=status.HTTP_400_BAD_REQUEST)
            
        user.set_password(new_password)
        user.save()
        
        return Response({'success': 'Şifre başarıyla güncellendi'})
        
    @action(detail=False, methods=['get'])
    def donation_history(self, request):
        user = request.user
        donations = BloodDonation.objects.filter(donor=user).order_by('-donation_date')
        
        from donations.serializers import BloodDonationSerializer
        serializer = BloodDonationSerializer(donations, many=True)
        
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def notification_settings(self, request):
        user = request.user
        notification_enabled = request.data.get('notification_enabled')
        
        if notification_enabled is not None:
            user.notification_enabled = notification_enabled
            user.save(update_fields=['notification_enabled'])
            return Response({'notification_enabled': user.notification_enabled})
            
        return Response({'error': 'notification_enabled alanı gereklidir'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Hesabınız başarıyla oluşturuldu!")
            return redirect('core:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        else:
            messages.error(request, "Kullanıcı adı veya şifre yanlış!")
    
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Çıkış yaptınız.")
    return redirect('core:home')

@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profiliniz güncellendi!")
            return redirect('users:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
        
    donation_history = BloodDonation.objects.filter(donor=request.user).order_by('-donation_date')
    can_donate = request.user.can_donate()
    days_until_next_donation = request.user.days_until_next_donation()
    
    context = {
        'form': form,
        'donation_history': donation_history,
        'can_donate': can_donate,
        'days_until_next_donation': days_until_next_donation,
    }
    
    return render(request, 'users/profile.html', context)
