from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    # Mark all as read
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
@require_POST
def mark_read(request, pk):
    try:
        notif = Notification.objects.get(pk=pk, recipient=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False}, status=404)


@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications:list')


@login_required
def notification_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})
