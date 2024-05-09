from django.core.paginator import Paginator
from django.utils import timezone

from .models import Post


# Константа для отображения 10 записей на главной странице.
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


# Пагинатор.
def get_paginator(posts, request):
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }
