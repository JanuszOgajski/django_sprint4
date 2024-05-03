from django.shortcuts import get_object_or_404, redirect

from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm
from django.urls import reverse


class PostMixin:
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if post.author != self.request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)


class CommentEditMixin:
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.get_object().post_id}
        )
