from django import forms

from .models import Post, User, Comment


class PostForm(forms.ModelForm):
    """Форма для поста."""

    class Meta:
        model = Post
        exclude = ('author', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M', attrs={
                    'type': 'datetime-local'
                }
            )
        }


class CommentForm(forms.ModelForm):
    """Форма для комментария."""

    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.ModelForm):
    """Форма для пользователя."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
