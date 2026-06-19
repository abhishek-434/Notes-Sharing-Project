from django import forms
from .models import Note, Comment


ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.zip']


class NoteUploadForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'subject', 'department', 'semester', 'description', 'file', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Data Structures Notes - Unit 1'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Data Structures and Algorithms'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe what this note covers...'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.ppt,.pptx,.zip'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. python, algorithms, semester3 (comma separated)'}),
        }
        labels = {
            'tags': 'Tags (comma separated)',
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}')
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError('File too large. Maximum size is 50MB.')
        return file


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...',
            }),
        }
        labels = {'content': ''}
