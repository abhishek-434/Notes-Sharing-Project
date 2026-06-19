from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notes.models import Note, NoteDownload
from forum.models import Question


@login_required
def dashboard_home(request):
    user = request.user
    my_notes = Note.objects.filter(uploader=user).order_by('-upload_date')
    total_uploads = my_notes.count()
    total_downloads = sum(note.download_count for note in my_notes)
    
    recent_uploads = my_notes[:5]
    recent_downloads = NoteDownload.objects.filter(
        note__uploader=user
    ).select_related('note', 'user').order_by('-downloaded_at')[:5]
    
    my_questions = Question.objects.filter(author=user).order_by('-created_at')[:5]
    
    # Download stats per note
    top_notes = my_notes.order_by('-download_count')[:5]
    
    context = {
        'total_uploads': total_uploads,
        'total_downloads': total_downloads,
        'recent_uploads': recent_uploads,
        'recent_downloads': recent_downloads,
        'my_questions': my_questions,
        'top_notes': top_notes,
        'approved_notes': my_notes.filter(status='approved').count(),
        'pending_notes': my_notes.filter(status='pending').count(),
    }
    return render(request, 'dashboard/dashboard.html', context)
