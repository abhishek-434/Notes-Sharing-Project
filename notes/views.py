from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import os
from .models import Note, NoteDownload, Comment, NoteRating
from .forms import NoteUploadForm, CommentForm
from notifications.models import Notification


def notes_list(request):
    notes = Note.objects.filter(status='approved').select_related('uploader', 'uploader__profile')
    
    # Search
    query = request.GET.get('q', '')
    department = request.GET.get('department', '')
    semester = request.GET.get('semester', '')
    sort = request.GET.get('sort', '-upload_date')
    
    if query:
        notes = notes.filter(
            Q(title__icontains=query) |
            Q(subject__icontains=query) |
            Q(description__icontains=query) |
            Q(uploader__username__icontains=query) |
            Q(uploader__profile__full_name__icontains=query)
        )
    
    if department:
        notes = notes.filter(department=department)
    
    if semester:
        notes = notes.filter(semester=semester)
    
    # Sorting
    sort_options = {
        '-upload_date': '-upload_date',
        'upload_date': 'upload_date',
        '-download_count': '-download_count',
        'title': 'title',
    }
    notes = notes.order_by(sort_options.get(sort, '-upload_date'))
    
    # Pagination
    paginator = Paginator(notes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    from notes.models import Note as NoteModel
    DEPARTMENT_CHOICES = NoteModel.department.field.choices if hasattr(NoteModel, 'department') else []
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'department': department,
        'semester': semester,
        'sort': sort,
        'total_count': notes.count(),
        'department_choices': [('BCA','BCA'),('MCA','MCA'),('BTECH','B.Tech'),('BBA','BBA'),('MBA','MBA'),('MTECH','M.Tech'),('OTHER','Others')],
        'semester_choices': [(str(i), f'Semester {i}') for i in range(1, 9)],
    }
    return render(request, 'notes/list.html', context)


def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, status='approved')
    note.view_count += 1
    note.save(update_fields=['view_count'])
    
    comments = note.comments.filter(parent=None, is_deleted=False).select_related('author', 'author__profile').prefetch_related('replies')
    comment_form = CommentForm()
    
    # Similar notes
    similar = Note.objects.filter(
        status='approved', department=note.department
    ).exclude(pk=pk).order_by('-download_count')[:4]
    
    # User rating
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = NoteRating.objects.get(note=note, user=request.user).rating
        except NoteRating.DoesNotExist:
            pass
    
    avg_rating = None
    ratings = note.ratings.all()
    if ratings.exists():
        avg_rating = sum(r.rating for r in ratings) / ratings.count()
    
    context = {
        'note': note,
        'comments': comments,
        'comment_form': comment_form,
        'similar_notes': similar,
        'user_rating': user_rating,
        'avg_rating': avg_rating,
        'rating_count': ratings.count(),
    }
    return render(request, 'notes/detail.html', context)


@login_required
def note_upload(request):
    if request.method == 'POST':
        form = NoteUploadForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.uploader = request.user
            note.save()
            form.save_m2m()
            messages.success(request, f'Note "{note.title}" uploaded successfully! 🎉')
            return redirect('notes:detail', pk=note.pk)
    else:
        form = NoteUploadForm()
    
    return render(request, 'notes/upload.html', {'form': form})


@login_required
def note_download(request, pk):
    note = get_object_or_404(Note, pk=pk, status='approved')
    
    try:
        file_path = note.file.path
        if not os.path.exists(file_path):
            messages.error(request, 'File not found.')
            return redirect('notes:detail', pk=pk)
        
        # Record download
        NoteDownload.objects.create(
            note=note,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        note.download_count += 1
        note.save(update_fields=['download_count'])
        
        # Notify uploader
        if request.user.is_authenticated and note.uploader != request.user:
            Notification.create_notification(
                recipient=note.uploader,
                sender=request.user,
                notification_type='download',
                message=f'{request.user.username} downloaded your note "{note.title}"',
                url=note.get_absolute_url()
            )
        
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return response
    
    except Exception as e:
        messages.error(request, 'Unable to download file. Please try again.')
        return redirect('notes:detail', pk=pk)


@login_required
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk, uploader=request.user)
    if request.method == 'POST':
        title = note.title
        note.delete()
        messages.success(request, f'Note "{title}" deleted successfully.')
        return redirect('dashboard:home')
    return render(request, 'notes/confirm_delete.html', {'note': note})


@login_required
@require_POST
def add_comment(request, pk):
    note = get_object_or_404(Note, pk=pk, status='approved')
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.note = note
        comment.author = request.user
        parent_id = request.POST.get('parent_id')
        if parent_id:
            try:
                comment.parent = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                pass
        comment.save()
        
        # Notify note owner
        if note.uploader != request.user:
            Notification.create_notification(
                recipient=note.uploader,
                sender=request.user,
                notification_type='comment',
                message=f'{request.user.username} commented on your note "{note.title}"',
                url=note.get_absolute_url()
            )
        
        messages.success(request, 'Comment added! ✅')
    return redirect('notes:detail', pk=pk)


@login_required
@require_POST
def rate_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    rating_val = int(request.POST.get('rating', 0))
    if 1 <= rating_val <= 5:
        NoteRating.objects.update_or_create(
            note=note, user=request.user,
            defaults={'rating': rating_val}
        )
        return JsonResponse({'success': True, 'rating': rating_val})
    return JsonResponse({'success': False})


def my_notes(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    notes = Note.objects.filter(uploader=request.user).order_by('-upload_date')
    return render(request, 'notes/my_notes.html', {'notes': notes})
