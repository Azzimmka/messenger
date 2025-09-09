# app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Message, Contact
from .forms import MessageForm

def home(request):
    return render(request, 'app/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'app/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})

def user_logout(request):
    auth_logout(request)
    return redirect('login')

@login_required
def contact_list(request):
    contacts = Contact.objects.filter(user=request.user)
    all_users = User.objects.exclude(id=request.user.id)  # Получаем всех пользователей, кроме текущего

    if request.method == 'POST':
        contact_user_id = request.POST.get('contact_user')
        if contact_user_id:
            try:
                contact_user = User.objects.get(id=contact_user_id)
                Contact.objects.get_or_create(user=request.user, contact_user=contact_user)
            except User.DoesNotExist:
                # Обработка ошибки при отсутствии пользователя
                pass
        return redirect('contact_list')

    return render(request, 'app/contact_list.html', {'contacts': contacts, 'all_users': all_users})

@login_required
def message_list(request):
    contact_id = request.GET.get('contact_id')
    contact_user = None
    messages_sent = []
    messages_received = []

    # Получение списка контактов пользователя
    contacts = Contact.objects.filter(user=request.user)
    contact_list = [contact.contact_user for contact in contacts]

    if contact_id:
        contact_user = get_object_or_404(User, id=contact_id)
        messages_sent = Message.objects.filter(sender=request.user, receiver=contact_user)
        messages_received = Message.objects.filter(sender=contact_user, receiver=request.user)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content and contact_user:
            Message.objects.create(sender=request.user, receiver=contact_user, content=content)
            return redirect(f'{request.path}?contact_id={contact_id}')

    return render(request, 'app/message_list.html', {
        'messages_sent': messages_sent,
        'messages_received': messages_received,
        'contact_user': contact_user,
        'contact_list': contact_list
    })

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
    return render(request, 'app/send_message.html', {'form': form})


from django.contrib.auth import authenticate, login as auth_login

def switch_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')  # Перенаправление на главную страницу после входа
    return render(request, 'app/switch_user.html')
