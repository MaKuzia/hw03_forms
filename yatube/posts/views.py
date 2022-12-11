from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm
from .models import Group, Post

from posts.utils import For_Paginator

User = get_user_model()


def index(request):
    template = 'posts/index.html'
    context = {
        'page_obj': For_Paginator(request, Post.objects.all()),
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_group = group.posts.all()
    context = {
        'group': group,

        ''' все комметарии УДАЛЮ!!
         к переменной posts_group обращаюсь в шаблоне,
         без неё посты не выводятся '''
        'posts_group': posts_group,
        'page_obj': For_Paginator(request, posts_group),
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    user_posts = author.posts.all()
    context = {
        'author': author,

        '''к user_posts тоже обращаюсь в шаблоне, без неё посты не выводятся'''
        'user_posts': user_posts,
        'page_obj': For_Paginator(request, user_posts),
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post_req = get_object_or_404(Post, pk=post_id)
    author = Post.objects.filter(author=post_req.author)
    context = {
        'post': post_req,
        # author - тоже обращаюсь в шаблоне, считаю кол-во постов автора
        'author': author,
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
    if request.user == current_post.author:
        form = PostForm(request.POST or None)
        if form.is_valid():
            '''оставила строки с 74-76, без них изменения поста не сохраняются,
             пробовала исправить - не получилось:('''
            edit_post = form.save(False)
            current_post.text = edit_post.text
            current_post.group = edit_post.group
            current_post.save(update_fields=['text', 'group'])
            return redirect('posts:post_detail', current_post.pk)
        form = PostForm(instance=current_post)
        context = {
            'form': form,
            'is_edit': True,
        }
        return render(request, template, context)
