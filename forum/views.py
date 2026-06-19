from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Question, Answer, ForumComment
from .forms import QuestionForm, AnswerForm, ForumCommentForm
from notifications.models import Notification


def forum_list(request):
    questions = Question.objects.select_related('author', 'author__profile').prefetch_related('answers')
    
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'latest')
    
    if query:
        questions = questions.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )
    
    if filter_type == 'unanswered':
        questions = questions.filter(answers__isnull=True)
    elif filter_type == 'resolved':
        questions = questions.filter(is_resolved=True)
    else:
        questions = questions.order_by('-created_at')
    
    paginator = Paginator(questions, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'filter_type': filter_type,
        'total_questions': Question.objects.count(),
    }
    return render(request, 'forum/list.html', context)


def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    question.views += 1
    question.save(update_fields=['views'])
    
    answers = question.answers.select_related('author', 'author__profile').prefetch_related('forum_comments')
    answer_form = AnswerForm()
    comment_form = ForumCommentForm()
    
    context = {
        'question': question,
        'answers': answers,
        'answer_form': answer_form,
        'comment_form': comment_form,
    }
    return render(request, 'forum/detail.html', context)


@login_required
def ask_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            form.save_m2m()
            messages.success(request, 'Question posted successfully! 🎉')
            return redirect('forum:detail', pk=question.pk)
    else:
        form = QuestionForm()
    return render(request, 'forum/ask.html', {'form': form})


@login_required
def post_answer(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()
            
            # Notify question author
            Notification.create_notification(
                recipient=question.author,
                sender=request.user,
                notification_type='answer',
                message=f'{request.user.username} answered your question "{question.title[:50]}"',
                url=question.get_absolute_url()
            )
            messages.success(request, 'Answer posted! ✅')
    return redirect('forum:detail', pk=pk)


@login_required
def upvote_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.user in answer.upvotes.all():
        answer.upvotes.remove(request.user)
        voted = False
    else:
        answer.upvotes.add(request.user)
        voted = True
    return JsonResponse({'voted': voted, 'count': answer.upvotes.count()})


@login_required
def accept_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk, question__author=request.user)
    answer.is_accepted = not answer.is_accepted
    answer.save()
    if answer.is_accepted:
        answer.question.is_resolved = True
        answer.question.save()
    return JsonResponse({'accepted': answer.is_accepted})
