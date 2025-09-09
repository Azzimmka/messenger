from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile-setup/', views.profile_setup, name='profile_setup'),
    path('profile/', views.profile_update, name='profile_update'),
    path('chat/', views.chat, name='chat'),
    path('add-contact/', views.add_contact, name='add_contact'),
    path('api/messages/', views.get_messages, name='get_messages'),
]
