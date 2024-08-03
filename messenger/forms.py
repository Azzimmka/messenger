# messenger/forms.py

from django import forms
from .models import Message
from django.contrib.auth.models import User
from .models import Contact
from django.contrib.auth.forms import UserCreationForm


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'content']


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['contact_user']
        widgets = {
            'contact_user': forms.Select(attrs={'class': 'form-control'}),
        }


