from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse

from .forms import UserForm, PostForm, CommentForm
from .models import Post, Category, User, Comment
from .utils import get_joined_models, get_filtered_posts

# Константа для хранения кол-ва страниц пагинации
PAGINATOR_QUANTITY = 10

# Константа для фильрации постов
P_FILTER = '-pub_date'


class BlogHome(ListView):
    """Отображение главной страницы."""

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = PAGINATOR_QUANTITY

    def get_queryset(self):
        """Получение списка постов с кол-во комментариев."""
        return get_filtered_posts(get_joined_models()).order_by(
            P_FILTER).annotate(comment_count=Count('comments'))


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


class CategoryPosts(ListView):
    """Отображение списка постов по категории."""

    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = PAGINATOR_QUANTITY

    def get_queryset(self):
        """Определяем категорию по слагу и возвращаем список постов."""
        posts = get_filtered_posts(get_joined_models(),
                                   category__slug=self.kwargs['category_slug'])
        posts = posts.order_by(
            P_FILTER).annotate(comment_count=Count('comments'))
        return posts

    def get_context_data(self, **kwargs):
        """Добавление модели категории в контекст шаблона."""
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True)
        return context


class Profile(ListView):
    """Отображение списка постов в профиле."""

    template_name = 'blog/profile.html'
    paginate_by = PAGINATOR_QUANTITY

    def get_queryset(self):
        """Получение списка постов."""
        posts = get_filtered_posts(get_joined_models(),
                                   author__username=self.kwargs['username'])
        posts = posts.order_by(
            P_FILTER).annotate(comment_count=Count('comments'))
        return posts

    def get_context_data(self, **kwargs):
        """Добавление объекта профиля."""
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

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={
                'profile': self.kwargs['profile']
            }
        )


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
