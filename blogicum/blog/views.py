from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .forms import UserForm, PostForm, CommentForm
from .models import Post, Category, User, Comment
from .mixins import ListOfPostMixin


class BlogHome(ListOfPostMixin):
    """Отображение главной страницы."""

    def get_queryset(self):
        """Получение списка постов с кол-во комментариев."""
        return self.queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True)


class PostDetail(DetailView):
    """Отображение подробного поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        """Добавление формы и модели комментариев."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CategoryPosts(ListOfPostMixin):
    """Отображение списка постов по категории."""

    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        """Добавление модели категории в контекст шаблона."""
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True)
        return context

    def get_queryset(self):
        """Определяем категорию по слагу и возвращаем список постов."""
        return (super().queryset.filter(
            category__slug=self.kwargs['category_slug'],
            is_published=True
        ))


class Profile(ListOfPostMixin):
    """Отображение списка постов в профиле."""

    template_name = 'blog/profile.html'

    def get_queryset(self):
        """Получение списка постов."""
        return self.queryset.filter(
                                   author__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        """Добавление объекта профиля."""
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            get_user_model(), username=self.kwargs['username']
        )
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.kwargs['username']})


class EditProfile(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={
                'username': self.request.user.username})


class CreatePost(LoginRequiredMixin, CreateView):
    """Создание поста."""
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Метод для переопределения формы, так как автор не указывается."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Метод для редиректа на страницу профиля."""
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username})


class EditPost(LoginRequiredMixin, UpdateView):
    """Редактирование поста."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return redirect('blog:post_detail', self.object.id)

    def form_valid(self, form):
        """Передача объекта автора в форму."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, id=post_id)


class DeletePost(LoginRequiredMixin, DeleteView):
    """Удаление поста."""

    template_name = 'blog/create.html'
    model = Post
    success_url = '/'

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, id=post_id)


class AddComment(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'comment.html'
    object = None

    def dispatch(self, request, *args, **kwargs):
        """Получение объекта поста по id."""
        self.object = get_object_or_404(
            Post,
            pk=kwargs['post_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Добавление в форму объектов автора и поста."""
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={
                'id': self.kwargs['post_id']
            }
        )


class EditComment(LoginRequiredMixin, UpdateView):
    """Редактирование комментария."""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={
                           'id': self.object.post.id
                       })

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, pk=comment_id)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DeleteComment(LoginRequiredMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    success_url = '/'

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, id=comment_id)
