from django.contrib import admin
from .models import Note, NoteDownload, Comment, NoteRating


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'department', 'semester', 'uploader', 'status', 'download_count', 'upload_date']
    list_filter = ['status', 'department', 'semester', 'upload_date']
    search_fields = ['title', 'subject', 'uploader__username']
    list_editable = ['status']
    readonly_fields = ['download_count', 'view_count', 'upload_date', 'updated_at']
    actions = ['approve_notes', 'reject_notes', 'feature_notes']
    date_hierarchy = 'upload_date'
    ordering = ['-upload_date']

    def approve_notes(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f'{count} note(s) approved successfully.')
    approve_notes.short_description = '✅ Approve selected notes'

    def reject_notes(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'{count} note(s) rejected.')
    reject_notes.short_description = '❌ Reject selected notes'

    def feature_notes(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} note(s) featured.')
    feature_notes.short_description = '⭐ Feature selected notes'


@admin.register(NoteDownload)
class NoteDownloadAdmin(admin.ModelAdmin):
    list_display = ['note', 'user', 'downloaded_at', 'ip_address']
    list_filter = ['downloaded_at']
    readonly_fields = ['downloaded_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'note', 'content', 'created_at', 'is_deleted']
    list_filter = ['is_deleted', 'created_at']
    actions = ['delete_comments']

    def delete_comments(self, request, queryset):
        queryset.update(is_deleted=True)
    delete_comments.short_description = 'Mark as deleted'


@admin.register(NoteRating)
class NoteRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'note', 'rating', 'created_at']
