from django import forms
from .models import Question, Answer, ForumComment


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What is your question?'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Describe your question in detail...'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. python, algorithms, database (comma separated)'}),
        }
        labels = {'tags': 'Tags (comma separated)'}


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your answer here...'}),
        }
        labels = {'body': 'Your Answer'}


class ForumCommentForm(forms.ModelForm):
    class Meta:
        model = ForumComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Add a comment...'}),
        }
        labels = {'content': ''}
