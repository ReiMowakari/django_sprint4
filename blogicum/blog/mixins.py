from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView
from django.urls import reverse

from .forms import CommentForm
from .models import Post, Comment

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


class EditDeletePost(LoginRequiredMixin):
    """Микс для редактирования и удаления постов"""

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        """Проверка на права для удаления чужих сущностей."""
        instance = get_object_or_404(
            Post, pk=kwargs['post_id']
        )
        if instance.author != request.user:
            return redirect('blog:post_detail',instance.pk)
        return super().dispatch(request, *args, **kwargs)


class EditDeleteComment(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        """Проверка на права для удаления чужих сущностей."""
        instance = get_object_or_404(
            Comment, pk=kwargs['comment_id']
        )
        if instance.author != request.user:
            raise PermissionDenied('Нет прав')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={
                'post_id': self.kwargs['post_id']}
        )
