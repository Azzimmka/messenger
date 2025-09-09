from django.db import models

# Create your models here.
# app/models.py

from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts', null=True)
    contact_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacted_by', null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.contact_user.username}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"
