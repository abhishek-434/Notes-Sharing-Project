from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


class Question(models.Model):
    title = models.CharField(max_length=300)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    tags = TaggableManager(blank=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('forum:detail', kwargs={'pk': self.pk})

    def answer_count(self):
        return self.answers.count()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    body = models.TextField()
    is_accepted = models.BooleanField(default=False)
    upvotes = models.ManyToManyField(User, blank=True, related_name='upvoted_answers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_accepted', '-created_at']

    def __str__(self):
        return f"Answer to: {self.question.title}"


class ForumComment(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='forum_comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_comments')
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username}"
