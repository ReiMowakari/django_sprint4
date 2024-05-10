from django.db.models import Count
from django.views.generic import ListView

from .models import Post

PAGINATOR_QUANTITY = 10
FROM_NEW_TO_OLD = '-pub_date'


class ListOfPostMixin(ListView):
    """Микс для формирования списка постов."""
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATOR_QUANTITY

    queryset = Post.objects.select_related(
        'category', 'location', 'author'
    ).annotate(comment_count=Count('comments')
               ).order_by(FROM_NEW_TO_OLD)
