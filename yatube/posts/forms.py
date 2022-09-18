from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_text = {
            'text': ('Текст поста'),
            'group': ('Группа, к которой относится пост'),
            'image': ('Прикрепите изображение'),
        }
        # Пытался во все записи добавить заголовок,
        # но, спустя пару часов миграций туда-сюда, сдался.
        # fields = ('title', 'text', 'group')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_text = {
            'text': ('Текст комментария')
        }