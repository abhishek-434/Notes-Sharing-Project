from django.db import models
from django.contrib.auth.models import User


NOTIFICATION_TYPES = [
    ('comment', 'Comment on Notes'),
    ('download', 'Note Downloaded'),
    ('answer', 'Answer to Question'),
    ('announcement', 'Announcement'),
    ('upload', 'New Note in Department'),
]


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=300)
    url = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:50]}"

    @classmethod
    def create_notification(cls, recipient, sender, notification_type, message, url=''):
        if recipient != sender:
            cls.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                message=message,
                url=url
            )
