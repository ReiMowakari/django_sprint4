from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import (
    DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .forms import UserForm, PostForm, CommentForm
from .models import Post, Category, User, Comment
from .mixins import ListOfPostMixin, EditDeletePost, EditDeleteComment


class BlogHome(ListOfPostMixin):
    """Отображение главной страницы."""

    def get_queryset(self):
        """Получение списка постов с фильтрацией."""
        return super().queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True)


class PostDetail(DetailView):
    """Отображение подробного поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Post, pk=kwargs['post_id'])
        if ((
                not obj.is_published or not obj.category.is_published
                or obj.pub_date > timezone.now())
                and obj.author != request.user):
            raise Http404('Страница не найдена')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Добавление формы и модели комментариев."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author'))
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
        return super().queryset.filter(
            category__slug=self.kwargs['category_slug'],
            is_published=True,
            pub_date__lte=timezone.now())


class Profile(ListOfPostMixin):
    """Отображение списка постов в профиле."""

    template_name = 'blog/profile.html'

    def get_queryset(self):
        """
        Получение списка всех постов
        или только опубликованных,
        в зависимости от перехода в свой
        или чужой профиль.
        """
        posts = super().queryset.filter(
            author__username=self.kwargs['username'])
        if self.request.user.username == self.kwargs['username']:
            return posts
        return posts.filter(is_published=True)

    def get_context_data(self, **kwargs):
        """Добавление объекта профиля в контекст."""
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            get_user_model(), username=self.kwargs['username']
        )
        return context


class EditProfile(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username})


class CreatePost(LoginRequiredMixin, CreateView):
    """Создание поста."""

    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """
        Метод для переопределения формы,
        так как автор не указывается.
        """
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Метод для редиректа на страницу профиля."""
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username})


class EditPost(EditDeletePost, UpdateView):
    """Редактирование поста."""

    form_class = PostForm


class DeletePost(EditDeletePost, DeleteView):
    """Удаление поста."""

    success_url = reverse_lazy('blog:index')


class AddComment(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'comment.html'

    def form_valid(self, form):
        """Добавление в форму объектов автора и существующего поста."""
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            id=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={
                'post_id': self.kwargs['post_id']
            }
        )


class EditComment(EditDeleteComment, UpdateView):
    """Редактирование комментария."""

    pass


class DeleteComment(EditDeleteComment, DeleteView):
    """Удаление комментария."""

    pass
