# messenger/urls.py

from django.urls import path
from . import views
# messenger/urls.py



urlpatterns = [
    path('', views.home, name='home'),
    path('contacts/', views.contact_list, name='contact_list'),
    path('contacts/add/', views.add_contact, name='add_contact'),
    path('messages/', views.message_list, name='message_list'),
    path('send/', views.send_message, name='send_message'),
    path('register/', views.register, name='register'),
    path('switch_user/', views.switch_user, name='switch_user'),
    path('logout/', views.logout, name='logout'), 
]
