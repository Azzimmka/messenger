# app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('contacts/', views.contact_list, name='contact_list'),
    path('messages/', views.message_list, name='message_list'),
    path('send_message/', views.send_message, name='send_message'),
    path('add_contact/', views.contact_list, name='add_contact'),
    path('switch_user/', views.switch_user, name='switch_user'),

]
