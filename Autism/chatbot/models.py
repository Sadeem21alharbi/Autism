from django.db import models

from django.contrib.auth.models import User



class Conversation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Conversation {self.id}"

class ChatMessage(models.Model):

    class MessageType(models.TextChoices):

        USER = 'user', 'User'

        AI = 'ai', 'AI'


    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    message_type = models.CharField(
        max_length=10,
        choices=MessageType.choices
    )

    content = models.TextField()

    confidence_score = models.FloatField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.content[:30]