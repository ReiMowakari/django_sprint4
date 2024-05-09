from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse

from .forms import UserForm, PostForm, CommentForm
from .models import Post, Category, User, Comment
from .utils import get_joined_models, get_filtered_posts, get_paginator


class BlogHome(ListView):
    """Отображение главной страницы."""
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self):
        return get_filtered_posts(get_joined_models()).order_by(
            '-pub_date').annotate(
        comment_count=Count('comment')
    )


class PostDetail(DetailView):
    """Отображение подробного поста."""
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related('author')
        )
        return context


class CategoryPosts(ListView):
    """Отображение списка постов по категории."""
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    allow_empty = False
    paginate_by = 10

    def get_queryset(self):
        """Определяем категорию по слагу и возвращаем список постов."""
        return get_filtered_posts(get_joined_models(),
                                  category__slug=self.kwargs['category_slug'],
                                  ).order_by('-pub_date').annotate(
                                  comment_count=Count('comment')
    )

    def get_context_data(self, **kwargs):
        """Добавление модели категории в контекст шаблона."""
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category,
                                                slug=self.kwargs['category_slug'])
        return context


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=profile
    ).order_by('-pub_date').annotate(
        comment_count=Count('comment')
    )
    context = {'profile': profile
               }
    context.update(get_paginator(posts, request))
    return render(request, 'blog/profile.html', context)


def edit_profile(request):
    instance = get_object_or_404(User, username=request.user)
    form = UserForm(request.POST, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, 'blog/user.html', context)


class CreatePost(LoginRequiredMixin, CreateView):
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


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'form': form, 'post': post, 'is_edit': True}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    instance = get_object_or_404(Post, id=post_id)
    form = PostForm(instance=instance)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=post_id)


def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = Comment.objects.get(pk=comment_id)
    if request.user != user.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(
        request.POST or None,
        files=request.FILES or None,
        instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {
        'form': form,
        'comment': comment,
        'is_edit': True}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, id=comment_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html')










