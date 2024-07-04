from django.contrib.auth.models import User
from django.db import models


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')

    def __str__(self):
        return f'Conversation {self.id}'

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Message from {self.sender} at {self.timestamp} in conv. {self.conversation}'

    class Meta:
        ordering = ['timestamp']