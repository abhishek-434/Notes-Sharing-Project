from django.contrib import admin
from .models import Question, Answer, ForumComment


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'answer_count', 'views', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['title', 'body', 'author__username']
    readonly_fields = ['views', 'created_at', 'updated_at']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'author', 'is_accepted', 'created_at']
    list_filter = ['is_accepted']


@admin.register(ForumComment)
class ForumCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'answer', 'content', 'created_at']
