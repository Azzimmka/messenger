from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max
from django.utils import timezone
from .models import Message, Contact, UserProfile
from .forms import SimpleRegistrationForm, SimpleLoginForm, MessageForm, ProfileUpdateForm

def home(request):
    if request.user.is_authenticated:
        return redirect('chat')
    return render(request, 'app/home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('chat')
        
    if request.method == 'POST':
        form = SimpleRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f'Welcome to Messenger, {user.userprofile.nickname}!')
            return redirect('profile_setup')
    else:
        form = SimpleRegistrationForm()
    return render(request, 'app/register_new.html', {'form': form})

@login_required
def profile_setup(request):
    """Allow users to customize their profile after registration"""
    if request.method == 'POST':
        return redirect('chat')
    return render(request, 'app/profile_setup.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('chat')
        
    if request.method == 'POST':
        form = SimpleLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Update online status
            if hasattr(user, 'userprofile'):
                user.userprofile.is_online = True
                user.userprofile.save()
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.userprofile.nickname}!')
            return redirect('chat')
    else:
        form = SimpleLoginForm()
    return render(request, 'app/login_new.html', {'form': form})

def user_logout(request):
    # Update online status
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        request.user.userprofile.is_online = False
        request.user.userprofile.save()
    auth_logout(request)
    return redirect('home')

@login_required
def chat(request):
    """Main chat interface combining contacts and messages"""
    contacts = Contact.objects.filter(user=request.user).select_related('contact_user__userprofile')
    all_users = User.objects.exclude(id=request.user.id).select_related('userprofile')
    
    contact_id = request.GET.get('contact_id')
    active_contact = None
    conversation = []
    
    if contact_id:
        active_contact = get_object_or_404(User, id=contact_id)
        # Get all messages between current user and selected contact
        conversation = Message.objects.filter(
            Q(sender=request.user, receiver=active_contact) |
            Q(sender=active_contact, receiver=request.user)
        ).order_by('timestamp')
        
        # Mark messages as read
        Message.objects.filter(
            sender=active_contact, 
            receiver=request.user,
            status='sent'
        ).update(status='read')
        
        # Auto-add contact if not already added and there are messages between them
        if conversation.exists():
            Contact.objects.get_or_create(
                user=request.user,
                contact_user=active_contact
            )
    
    # Handle new message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content and active_contact:
            # Create the message
            Message.objects.create(
                sender=request.user,
                receiver=active_contact,
                content=content
            )
            # Auto-add contact for both users if not already added
            Contact.objects.get_or_create(
                user=request.user,
                contact_user=active_contact
            )
            Contact.objects.get_or_create(
                user=active_contact,
                contact_user=request.user
            )
            return redirect(f'/chat/?contact_id={contact_id}')
    
    # Get all users who have had conversations with current user (for contact list)
    conversation_users = User.objects.filter(
        Q(sent_messages__receiver=request.user) |
        Q(received_messages__sender=request.user)
    ).exclude(id=request.user.id).distinct().select_related('userprofile')
    
    # Combine explicit contacts with conversation partners
    all_contact_users = set()
    contacts_with_info = []
    
    # Add explicit contacts
    for contact in contacts:
        all_contact_users.add(contact.contact_user.id)
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=contact.contact_user) |
            Q(sender=contact.contact_user, receiver=request.user)
        ).order_by('-timestamp').first()
        
        unread_count = Message.objects.filter(
            sender=contact.contact_user,
            receiver=request.user,
            status='sent'
        ).count()
        
        contacts_with_info.append({
            'contact': contact,
            'user': contact.contact_user,
            'last_message': last_message,
            'unread_count': unread_count,
            'is_explicit_contact': True
        })
    
    # Add conversation partners who aren't explicit contacts
    for user in conversation_users:
        if user.id not in all_contact_users:
            last_message = Message.objects.filter(
                Q(sender=request.user, receiver=user) |
                Q(sender=user, receiver=request.user)
            ).order_by('-timestamp').first()
            
            unread_count = Message.objects.filter(
                sender=user,
                receiver=request.user,
                status='sent'
            ).count()
            
            contacts_with_info.append({
                'contact': None,
                'user': user,
                'last_message': last_message,
                'unread_count': unread_count,
                'is_explicit_contact': False
            })
    
    # Sort by last message timestamp
    contacts_with_info.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else timezone.now() - timezone.timedelta(days=365),
        reverse=True
    )
    
    return render(request, 'app/chat.html', {
        'contacts_with_info': contacts_with_info,
        'all_users': all_users,
        'active_contact': active_contact,
        'conversation': conversation,
    })

@login_required
def add_contact(request):
    if request.method == 'POST':
        contact_user_id = request.POST.get('contact_user')
        if contact_user_id:
            try:
                contact_user = User.objects.get(id=contact_user_id)
                contact, created = Contact.objects.get_or_create(
                    user=request.user, 
                    contact_user=contact_user
                )
                if created:
                    messages.success(request, f'Added {contact_user.userprofile.nickname} to your contacts!')
                else:
                    messages.info(request, f'{contact_user.userprofile.nickname} is already in your contacts.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
    
    return redirect('chat')

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('chat')
    else:
        form = ProfileUpdateForm(instance=request.user.userprofile)
    
    return render(request, 'app/profile_update.html', {'form': form})

@login_required
def get_messages(request):
    """API endpoint for real-time message updates"""
    contact_id = request.GET.get('contact_id')
    if not contact_id:
        return JsonResponse({'messages': []})
    
    try:
        contact_user = User.objects.get(id=contact_id)
        messages_data = Message.objects.filter(
            Q(sender=request.user, receiver=contact_user) |
            Q(sender=contact_user, receiver=request.user)
        ).order_by('timestamp')
        
        messages_list = [{
            'sender': msg.sender.userprofile.nickname,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_mine': msg.sender == request.user,
            'status': msg.status
        } for msg in messages_data]
        
        return JsonResponse({'messages': messages_list})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Contact not found'}, status=404)
