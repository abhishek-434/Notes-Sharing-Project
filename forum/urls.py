from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_list, name='list'),
    path('<int:pk>/', views.question_detail, name='detail'),
    path('ask/', views.ask_question, name='ask'),
    path('<int:pk>/answer/', views.post_answer, name='answer'),
    path('answer/<int:pk>/upvote/', views.upvote_answer, name='upvote'),
    path('answer/<int:pk>/accept/', views.accept_answer, name='accept'),
]
