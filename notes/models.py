from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager
import os

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

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]


def note_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    safe_name = "".join(c for c in instance.title if c.isalnum() or c in (' ', '-', '_'))[:30]
    return f'notes/{instance.department}/{safe_name}{ext}'


class Note(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES)
    description = models.TextField(max_length=1000, blank=True)
    file = models.FileField(upload_to=note_upload_path)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_notes')
    upload_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    tags = TaggableManager(blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('notes:detail', kwargs={'pk': self.pk})

    def get_file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()

    def get_file_size(self):
        try:
            size = self.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size/1024:.1f} KB"
            else:
                return f"{size/(1024*1024):.1f} MB"
        except Exception:
            return "Unknown"

    def get_file_icon(self):
        ext = self.get_file_extension()
        icons = {
            '.pdf': 'bi-file-earmark-pdf-fill text-danger',
            '.doc': 'bi-file-earmark-word-fill text-primary',
            '.docx': 'bi-file-earmark-word-fill text-primary',
            '.ppt': 'bi-file-earmark-ppt-fill text-warning',
            '.pptx': 'bi-file-earmark-ppt-fill text-warning',
            '.zip': 'bi-file-earmark-zip-fill text-secondary',
        }
        return icons.get(ext, 'bi-file-earmark-fill')


class NoteDownload(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='downloads')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-downloaded_at']

    def __str__(self):
        return f"{self.note.title} downloaded"


class Comment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.note.title}"


class NoteRating(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('note', 'user')

    def __str__(self):
        return f"{self.user.username} rated {self.note.title}: {self.rating}"
