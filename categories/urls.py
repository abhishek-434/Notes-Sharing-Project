from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.categories_list, name='list'),
    path('<str:department>/', views.department_notes, name='department'),
]
