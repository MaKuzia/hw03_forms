from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def ForPaginator(request, list_object):
    paginator = Paginator(list_object, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    template = 'posts/index.html'
    context = {
        'page_obj': ForPaginator(request, Post.objects.all()),
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_group = group.posts.all()
    context = {
        'group': group,
        'posts_group': posts_group,
        'page_obj': ForPaginator(request, posts_group),
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    user_posts = author.posts.all()
    context = {
        'author': author,
        'user_posts': user_posts,
        'page_obj': ForPaginator(request, user_posts),
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post_req = get_object_or_404(Post, pk=post_id)
    author = Post.objects.filter(author=post_req.author)
    context = {
        'post': post_req,
        'author': author,
    }
    return render(request, template, context)

@login_required
def post_create(request):
    form = PostForm
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author.username)
        context = {
            'form': form,
        }
        return render(request, template, context)
    form = PostForm()
    return render(request, template, {'form': form})

@login_required
def post_edit(request, post_id):
    current_post = get_object_or_404(Post, pk=post_id)
    template = 'posts/create_post.html'
    is_edit = True
    if request.method == 'POST':
        form = PostForm(request.POST, instance=current_post)
        if form.is_valid():
            edit_post = form.save(False)
            current_post.text = edit_post.text
            current_post.group = edit_post.group
            current_post.save(update_fields=['text', 'group'])
            return redirect('posts:post_detail', current_post.pk)
    form = PostForm(instance=current_post)
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)
