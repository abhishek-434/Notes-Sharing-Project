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
    
    # Enrich categories for high-quality home page layout
    from categories.views import DEPARTMENTS
    category_meta = {
        'BCA': {
            'icon': 'bi-code-slash',
            'desc': 'Web Dev, DBMS, Programming',
            'grad': 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
            'icon_bg': 'rgba(99, 102, 241, 0.15)'
        },
        'MCA': {
            'icon': 'bi-terminal',
            'desc': 'Data Structures, AI, Cloud',
            'grad': 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
            'icon_bg': 'rgba(139, 92, 246, 0.15)'
        },
        'BTECH': {
            'icon': 'bi-cpu',
            'desc': 'Logic, Hardware, Architecture',
            'grad': 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
            'icon_bg': 'rgba(6, 182, 212, 0.15)'
        },
        'MTECH': {
            'icon': 'bi-braces-asterisk',
            'desc': 'Advanced Research & Systems',
            'grad': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
            'icon_bg': 'rgba(239, 68, 68, 0.15)'
        },
        'BBA': {
            'icon': 'bi-bar-chart-line',
            'desc': 'Marketing, Finance, Business',
            'grad': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            'icon_bg': 'rgba(16, 185, 129, 0.15)'
        },
        'MBA': {
            'icon': 'bi-briefcase',
            'desc': 'Strategy, HR, Leadership',
            'grad': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            'icon_bg': 'rgba(245, 158, 11, 0.15)'
        }
    }
    
    categories = []
    for key, meta in category_meta.items():
        if key in DEPARTMENTS:
            info = DEPARTMENTS[key]
            count = Note.objects.filter(status='approved', department=key).count()
            categories.append({
                'key': key,
                'name': info['name'],
                'full_name': info['full_name'],
                'color': info['color'],
                'count': count,
                'icon': meta['icon'],
                'desc': meta['desc'],
                'grad': meta['grad'],
                'icon_bg': meta['icon_bg'],
            })

    context = {
        'featured_notes': featured_notes,
        'latest_notes': latest_notes,
        'categories': categories,
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
