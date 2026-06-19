from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .forms import CustomRegistrationForm, CustomLoginForm, ProfileUpdateForm
from .models import UserProfile
from notes.models import Note


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Active by default for dev; set False for email verify
            user.save()
            
            # Generate verification token
            token = get_random_string(64)
            user.profile.verification_token = token
            user.profile.full_name = form.cleaned_data.get('full_name', '')
            user.profile.college_name = form.cleaned_data.get('college_name', '')
            user.profile.save()
            
            # Send verification email
            verify_url = request.build_absolute_uri(f'/accounts/verify-email/{token}/')
            try:
                send_mail(
                    'Verify your NotesHub account',
                    f'Hi {user.username},\n\nClick the link below to verify your email:\n{verify_url}\n\nIf you did not create this account, please ignore this email.\n\nTeam NotesHub',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            
            login(request, user)
            messages.success(request, f'Welcome to NotesHub, {user.username}! 🎉 Please check your email to verify your account.')
            return redirect('dashboard:home')
    else:
        form = CustomRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}! 👋')
                next_url = request.GET.get('next', 'dashboard:home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = CustomLoginForm(request)
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out. See you soon! 👋')
    return redirect('core:home')


def verify_email(request, token):
    try:
        profile = UserProfile.objects.get(verification_token=token)
        profile.email_verified = True
        profile.verification_token = ''
        profile.save()
        messages.success(request, 'Email verified successfully! ✅')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
    return redirect('dashboard:home')


@login_required
def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user
    
    profile = get_object_or_404(UserProfile, user=profile_user)
    user_notes = Note.objects.filter(uploader=profile_user, status='approved').order_by('-upload_date')
    total_downloads = sum(note.download_count for note in user_notes)
    
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'user_notes': user_notes[:6],
        'total_uploads': user_notes.count(),
        'total_downloads': total_downloads,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Update user's name
            request.user.first_name = profile.full_name.split(' ')[0] if profile.full_name else ''
            request.user.last_name = ' '.join(profile.full_name.split(' ')[1:]) if profile.full_name else ''
            request.user.save()
            messages.success(request, 'Profile updated successfully! ✅')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


def forgot_password_view(request):
    from django.contrib.auth.forms import PasswordResetForm
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='accounts/password_reset_email.html',
            )
            messages.success(request, 'Password reset email sent! Check your inbox.')
            return redirect('accounts:login')
    else:
        form = PasswordResetForm()
        form.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your email'})
    return render(request, 'accounts/forgot_password.html', {'form': form})
