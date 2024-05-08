from django import forms

from .models import Post, User, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',
                   'location',
                   'category'
                   )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = ('groups', 'user_permissions', 'is_staff',
                             'is_active', 'is_superuser', 'date_joined',
                             'last_login', 'password')
