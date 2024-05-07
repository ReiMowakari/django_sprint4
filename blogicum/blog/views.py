from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import UserForm, PostForm, CommentForm
from .models import Post, Category, User, Comment

# Константа для отображения 5 записей на главной странице.
POSTS_PER_PAGE = 10


# Функция объединения моделей.
def get_joined_models():
    return Post.objects.select_related(
        'location',
        'author',
        'category'
    )


# Функция фильтрации постов.
def get_filtered_posts(posts, **kwargs):
    return posts.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
        **kwargs
    )


def index(request):
    """функция отображения главной страницы проекта."""
    template_name = 'blog/index.html'
    posts = get_filtered_posts(get_joined_models()).order_by(
        '-pub_date')[:POSTS_PER_PAGE]
    context = {
        'posts': posts,
    }
    return render(request, template_name, context)


def post_detail(request, id):
    """функция отображения страницы с отдельной публикацией."""
    template_name = 'blog/detail.html'
    post = get_object_or_404(
        get_filtered_posts(get_joined_models()),
        pk=id,
    )
    context = {
        'post': post
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    """функция отображения страницы категории."""
    template_name = 'blog/category.html'
    # Определяем категорию по слагу. Если категории нет и неопубликована - 404.
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    # Получение списка постов по отфильтрованной категории.
    posts = get_filtered_posts(get_joined_models(), category_id=category)
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, template_name, context)


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


@login_required
def create_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', context)


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
def add_comment(request, post_id, comment_id=None):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        if comment_id:
            form = CommentForm(
                instance=Comment.objects.get(id=comment_id),
                data=request.POST
            )
        else:
            form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


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


def get_paginator(posts, request):
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }









