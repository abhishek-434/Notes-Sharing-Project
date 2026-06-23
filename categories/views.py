from django.shortcuts import render, get_object_or_404
from notes.models import Note

DEPARTMENTS = {
    'BCA': {'name': 'BCA', 'full_name': 'Bachelor of Computer Applications', 'color': '#0c5adb'},
    'MCA': {'name': 'MCA', 'full_name': 'Master of Computer Applications',  'color': '#1d4ed8'},
    'BTECH': {'name': 'B.Tech', 'full_name': 'Bachelor of Technology', 'color': '#00d2ff'},
    'BBA': {'name': 'BBA', 'full_name': 'Bachelor of Business Administration', 'color': '#93c5fd'},
    'MBA': {'name': 'MBA', 'full_name': 'Master of Business Administration',  'color': '#4facfe'},
    'MTECH': {'name': 'M.Tech', 'full_name': 'Master of Technology',  'color': '#1e3a8a'},
    'OTHER': {'name': 'Others', 'full_name': 'Other Courses',  'color': '#64748b'},
}


def categories_list(request):
    categories = []
    for key, info in DEPARTMENTS.items():
        count = Note.objects.filter(status='approved', department=key).count()
        categories.append({**info, 'key': key, 'count': count})
    
    return render(request, 'categories/list.html', {'categories': categories})


def department_notes(request, department):
    dept_info = DEPARTMENTS.get(department.upper())
    if not dept_info:
        from django.http import Http404
        raise Http404
    
    notes = Note.objects.filter(status='approved', department=department.upper()).order_by('-upload_date')
    semester = request.GET.get('semester', '')
    if semester:
        notes = notes.filter(semester=semester)
    
    from django.core.paginator import Paginator
    paginator = Paginator(notes, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'dept_info': dept_info,
        'department': department.upper(),
        'page_obj': page_obj,
        'semester': semester,
        'semester_choices': [(str(i), f'Semester {i}') for i in range(1, 9)],
    }
    return render(request, 'categories/department.html', context)
