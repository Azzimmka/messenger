# messenger/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import Contact, Message
from .forms import MessageForm, ContactForm 
from django.contrib.auth import logout as auth_logout

from django.http import HttpResponseNotAllowed


@login_required
def home(request):
    return render(request, 'messenger/home.html')



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('contact_list')
    else:
        form = UserCreationForm()
    return render(request, 'messenger/register.html', {'form': form})


@login_required
def contact_list(request):
    contacts = Contact.objects.filter(user=request.user)
    return render(request, 'messenger/contact_list.html', {'contacts': contacts})


@login_required
def message_list(request):
    messages = Message.objects.filter(recipient=request.user)
    return render(request, 'messenger/message_list.html', {'messages': messages})

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('message_list')
    else:
        form = MessageForm()
    return render(request, 'messenger/send_message.html', {'form': form})



@login_required
def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            return redirect('contact_list')
    else:
        form = ContactForm()
    return render(request, 'messenger/add_contact.html', {'form': form})





from django.contrib.auth import authenticate, login as auth_login

def switch_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')  # Перенаправление на главную страницу после входа
    return render(request, 'messenger/switch_user.html')




def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        return redirect('home')
    return HttpResponseNotAllowed(['POST'])

