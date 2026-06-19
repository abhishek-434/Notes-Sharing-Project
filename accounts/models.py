from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

DEPARTMENT_CHOICES = [
    ('BCA', 'BCA'),
    ('MCA', 'MCA'),
    ('BTECH', 'B.Tech'),
    ('BBA', 'BBA'),
    ('MBA', 'MBA'),
    ('MTECH', 'M.Tech'),
    ('OTHER', 'Others'),
]

SEMESTER_CHOICES = [
    ('1', 'Semester 1'),
    ('2', 'Semester 2'),
    ('3', 'Semester 3'),
    ('4', 'Semester 4'),
    ('5', 'Semester 5'),
    ('6', 'Semester 6'),
    ('7', 'Semester 7'),
    ('8', 'Semester 8'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True)
    college_name = models.CharField(max_length=200, blank=True)
    course = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, blank=True)
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default_avatar.png'

    def get_display_name(self):
        return self.full_name or self.user.get_full_name() or self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
