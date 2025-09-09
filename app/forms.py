from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Message, UserProfile
import random

class SimpleRegistrationForm(forms.Form):
    nickname = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your nickname (e.g., John, Alice, Mike)'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Create a simple password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm your password'
        })
    )
    avatar_emoji = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '😊',
            'style': 'font-size: 2rem; text-align: center;'
        }),
        required=False
    )
    
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if UserProfile.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError('This nickname is already taken. Please choose another one.')
        return nickname
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data
    
    def save(self):
        # Create a unique username based on nickname + random number
        nickname = self.cleaned_data['nickname']
        username = f"{nickname.lower()}_{random.randint(1000, 9999)}"
        
        # Ensure username is unique
        while User.objects.filter(username=username).exists():
            username = f"{nickname.lower()}_{random.randint(1000, 9999)}"
        
        user = User.objects.create_user(
            username=username,
            password=self.cleaned_data['password']
        )
        
        # Update the profile with the chosen nickname and emoji
        profile = user.userprofile
        profile.nickname = nickname
        profile.avatar_emoji = self.cleaned_data.get('avatar_emoji') or '😊'
        profile.save()
        
        return user

class SimpleLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your nickname or username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your password'
        })
    )
    
    def clean_username(self):
        username_or_nickname = self.cleaned_data.get('username')
        
        # Try to find user by nickname first, then by username
        try:
            profile = UserProfile.objects.get(nickname=username_or_nickname)
            return profile.user.username
        except UserProfile.DoesNotExist:
            # If not found by nickname, return as is (might be username)
            return username_or_nickname

class MessageForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Type your message here...',
            'style': 'resize: none; border-radius: 25px;'
        })
    )
    
    class Meta:
        model = Message
        fields = ['content']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nickname', 'avatar_emoji', 'theme_preference']
        widgets = {
            'nickname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your display name'
            }),
            'avatar_emoji': forms.TextInput(attrs={
                'class': 'form-control text-center',
                'style': 'font-size: 2rem;',
                'placeholder': '😊'
            }),
            'theme_preference': forms.Select(attrs={
                'class': 'form-control'
            })
        }
