from django.urls import path

from blog.views import (
    index,
    category_posts,
    PostCreateView,
    EditPostView,
    DeletePostView,
    PostDetailView,
    ProfileListView,
    EditProfileUpdateView,
    CommentCreateView,
    CommentDeleteView,
    CommentUpdateView
)

app_name = 'blog'

urlpatterns = [
    path('', index, name='index'),
    path(
        'category/<slug:category_slug>/',
        category_posts,
        name='category_posts'
    ),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path(
        'posts/<int:post_id>/edit/',
        EditPostView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        DeletePostView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/',
        PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'profile/edit/',
        EditProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<slug:username>/',
        ProfileListView.as_view(),
        name='profile'
    ),
    path(
        'posts/<int:post_id>/comment/',
        CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        CommentDeleteView.as_view(),
        name='delete_comment'
    )
]
