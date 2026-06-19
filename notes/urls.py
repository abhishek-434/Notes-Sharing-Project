from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.notes_list, name='list'),
    path('<int:pk>/', views.note_detail, name='detail'),
    path('upload/', views.note_upload, name='upload'),
    path('<int:pk>/download/', views.note_download, name='download'),
    path('<int:pk>/delete/', views.delete_note, name='delete'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('<int:pk>/rate/', views.rate_note, name='rate'),
    path('my-notes/', views.my_notes, name='my_notes'),
]
