from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=150, required=False)
    college_name = forms.CharField(max_length=200, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'college_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email'
        self.fields['full_name'].widget.attrs['placeholder'] = 'Your full name'
        self.fields['college_name'].widget.attrs['placeholder'] = 'Your college/university name'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = user.profile
            profile.full_name = self.cleaned_data.get('full_name', '')
            profile.college_name = self.cleaned_data.get('college_name', '')
            profile.save()
        return user


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username or Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'full_name', 'college_name', 'course', 'department', 'semester', 'bio']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'college_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'College/University Name'}),
            'course': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course (e.g. Computer Science)'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell something about yourself...'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
