from django.contrib.auth.decorators import login_required
from django.urls import path


from . import views

app_name = 'blog'


urlpatterns = [
    path('', views.BlogHome.as_view(), name='index'),
    path('posts/<int:id>/', views.PostDetail.as_view(), name='post_detail'),
    path(
        '<slug:category_slug>/',
        views.CategoryPosts.as_view(),
        name='category_posts'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path(
        'posts/create/',
        login_required(views.CreatePost.as_view()),
        name='create_post'),
    path(
        'posts/<int:post_id>/edit/',
        login_required(views.EditPost.as_view()),
        name='edit_post'),
    path(
        'posts/<int:post_id>/delete/',
        login_required(views.DeletePost.as_view()),
        name='delete_post'),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.delete_comment, name='delete_comment'),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>',
        views.edit_comment, name='edit_comment'),
]
