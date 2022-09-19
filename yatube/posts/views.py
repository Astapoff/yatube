from xml.dom import ValidationErr

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from .utils import my_paginator


def index(request):
    """Главная страница сайта"""
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = my_paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug=None):
    """Страница постов определенной группы"""
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.select_related('author', 'group').all()
    page_obj = my_paginator(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Страница профайла пользователя, его посты"""
    author = get_object_or_404(User, username=username)
    template = 'posts/profile.html'
    profile_list = author.posts.all()
    page_obj = my_paginator(request, profile_list)
    following = (
        request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=author).exists())
    context = {
        'author': author,
        'page_obj': page_obj,
        'profile_list': profile_list,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница отдельного поста, детали поста"""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.all().filter(post__id=post_id)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Страница с формой создания поста"""
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user)
        return render(request, template, {'form': form})
    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """Страница с формой редактирования поста"""
    template = 'posts/create_post.html'
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        if request.user == post.author:
            form = PostForm(
                request.POST,
                files=request.FILES or None,
                instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                return redirect('posts:post_detail', post_id=post_id)
        raise ValidationErr('Вы не можете редактировать чужие посты!')
    else:
        form = PostForm(instance=post)
    context = {
        'form': form,
        'is_edit': is_edit
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Создаёт страницу с постами авторов,
    на которых подписан пользователь"""
    user = request.user
    following_list = Post.objects.select_related(
        'author', 'group').filter(
            author__following__user=user)
    page_obj = my_paginator(request, following_list)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Создаёт подписку пользователя на автора постов"""
    guest = request.user
    author = get_object_or_404(User, username=username)
    if guest != author:
        Follow.objects.get_or_create(
            user=guest,
            author=author
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Отменяет подписку на автора"""
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if follower.exists():
        follower.delete()
    return redirect('posts:follow_index')
