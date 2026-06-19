from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from notes.models import Note
from forum.models import Question


def home(request):
    featured_notes = Note.objects.filter(status='approved', is_featured=True).order_by('-upload_date')[:6]
    latest_notes = Note.objects.filter(status='approved').order_by('-upload_date')[:8]
    total_notes = Note.objects.filter(status='approved').count()
    total_questions = Question.objects.count()
    
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    
    from notes.models import NoteDownload
    total_downloads = NoteDownload.objects.count()
    
    context = {
        'featured_notes': featured_notes,
        'latest_notes': latest_notes,
        'stats': {
            'notes': total_notes,
            'users': total_users,
            'downloads': total_downloads,
            'questions': total_questions,
        }
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        try:
            send_mail(
                f'NotesHub Contact: {subject}',
                f'From: {name} <{email}>\n\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER or 'admin@noteshub.com'],
                fail_silently=True,
            )
        except Exception:
            pass
        
        messages.success(request, 'Your message has been sent! We will get back to you soon. 📧')
        return redirect('core:contact')
    
    return render(request, 'core/contact.html')


def privacy(request):
    return render(request, 'core/privacy.html')


def terms(request):
    return render(request, 'core/terms.html')


def handler404(request, exception):
    return render(request, 'core/404.html', status=404)


def handler500(request):
    return render(request, 'core/500.html', status=500)
