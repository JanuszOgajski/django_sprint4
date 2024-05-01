from django.core.paginator import Paginator
from django.db.models import Count
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from blog.models import Post, Category, User, Comment
from blog.mixins import PostMixin
from blog.forms import PostForm, CommentForm
from blog.constants import NEW_POSTS


def index(request):
    post_list = Post.post_manager.all().order_by(
        '-pub_date').annotate(comment_count=Count('comments'))
    paginator = Paginator(post_list, NEW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'blog/index.html',
        {'page_obj': page_obj},
    )


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = category.posts(manager='post_manager').select_related(
        'location', 'category', 'author')
    paginator = Paginator(post_list, NEW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, template, context)


@login_required
def post_create(request):
    template_name = 'blog/create.html'
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            'blog:profile',
            kwargs={'username': request.user}
        )
    return render(request, template_name, {'form': form})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class EditPostView(LoginRequiredMixin, PostMixin, UpdateView):
    pass


class DeletePostView(LoginRequiredMixin, PostMixin, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostDetailView(DetailView):
    pk_url_kwarg = 'post_id'
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):  # я не знаю как иначе сделать
        post = get_object_or_404(
            Post.objects,
            id=self.kwargs[self.pk_url_kwarg]
        )
        if post.author_id == self.request.user.pk:
            return post
        else:
            return get_object_or_404(
                Post.post_manager,
                id=self.kwargs[self.pk_url_kwarg]
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = NEW_POSTS
    ordering = ['pub_date']
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_queryset(self):
        username = self.kwargs.get('username')
        author = get_object_or_404(User, username=username)
        if self.request.user == author:
            return Post.objects.select_related(
                'category', 'author', 'location'
            ).filter(
                author__username=username,
            ).order_by('-pub_date').annotate(comment_count=Count('comments'))
        else:
            return Post.post_manager.filter(
                author=author
            ).order_by('-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        # user  # get_object_or_404(User, username=self.kwargs.get('username'))
        context['profile'] = user
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'username': self.kwargs[self.request.user]}
        )


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        return self.request.user

    def test_func(self):
        object = self.get_object()
        return object.username == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.pk_url_kwarg]}
        )


class CommentUpdateView(UserPassesTestMixin, UpdateView):
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


class CommentDeleteView(UserPassesTestMixin, DeleteView):
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
