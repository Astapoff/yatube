from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_text = {
            'text': ('Текст поста'),
            'group': ('Группа, к которой относится пост'),
            'image': ('Прикрепите изображение'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_text = {
            'text': ('Текст комментария')
        }
