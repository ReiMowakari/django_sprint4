from .models import Post

from django.utils import timezone


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
