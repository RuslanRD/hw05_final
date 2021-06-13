from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    class Meta(object):
        model = Comment
        fields = ['text']
        labels = {'text': 'Текс комментария'}
        help_text = {'text': 'Пиши комментарий здесь'}
        widgets = {'text': forms.Textarea({'rows': 3})}
