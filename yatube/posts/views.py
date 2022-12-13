from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm
from .models import Group, Post
from posts.utils import paginate_posts

User = get_user_model()


def index(request):
    template = 'posts/index.html'
    context = {
        'page_obj': paginate_posts(request, Post.objects.all()),
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_group = group.posts.all()
    context = {
        'group': group,
        'page_obj': paginate_posts(request, posts_group),
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    user_posts = author.posts.all()
    context = {
        'author': author,
        'page_obj': paginate_posts(request, user_posts),
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post_req = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post_req,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    current_post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=current_post)
    if request.user != current_post.author:
        return redirect('posts:post_detail', current_post.pk)
    if form.is_valid():
        current_post.save()
        return redirect('posts:post_detail', current_post.pk)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)
