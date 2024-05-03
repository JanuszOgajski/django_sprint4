from django.core.paginator import Paginator
from django.db.models import Count
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from blog.models import Post, Category, User
from blog.mixins import PostMixin, CommentEditMixin
from blog.forms import PostForm, CommentForm
from blog.constants import POSTS_BY_PAGE


def paginator_obj(post_list):
    return Paginator(post_list, POSTS_BY_PAGE)


def order_and_comments(self):
    return self.order_by(
        '-pub_date').annotate(comment_count=Count('comments'))


def index(request):
    post_list = order_and_comments(Post.published_objects.all())
    page_number = request.GET.get('page')
    page_obj = paginator_obj(post_list).get_page(page_number)
    return render(
        request,
        'blog/index.html',
        {'page_obj': page_obj},
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = category.posts(manager='published_objects').select_related(
        'location', 'category', 'author')
    page_number = request.GET.get('page')
    page_obj = paginator_obj(post_list).get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, 'blog/category.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if not form.is_valid():
        return redirect(
            'blog:profile',
            kwargs={'username': request.user}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return render(request, 'blog/create.html', {'form': form})


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

    def get_object(self):
        post = get_object_or_404(
            Post.objects,
            id=self.kwargs[self.pk_url_kwarg]
        )
        if post.author == self.request.user:
            return post
        return get_object_or_404(
            Post.published_objects,
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
    paginate_by = POSTS_BY_PAGE
    ordering = ['pub_date']
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_author(self):
        username = self.kwargs.get('username')
        author = get_object_or_404(User, username=username)
        return author

    def get_queryset(self):
        if self.request.user == self.get_author():
            query = Post.objects.select_related(
                'category', 'author', 'location'
            )
        else:
            query = Post.published_objects
        return order_and_comments(
            query.filter(author=self.get_author())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
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
        user = self.get_object()
        return user == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(CommentEditMixin, LoginRequiredMixin, CreateView):
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(CommentEditMixin, UserPassesTestMixin, UpdateView):
    pass


class CommentDeleteView(CommentEditMixin, UserPassesTestMixin, DeleteView):
    pass
