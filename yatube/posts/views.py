from xml.dom import ValidationErr

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow

# Глобальная константа, определяющая количество последних записей.
COUNT_LAST_POSTS = 10


def index(request):
    # Шаблон стартовой страницы index.html
    template = 'posts/index.html'
    # Текст основного заголовка стартовой страницы
    home = 'Это главная страница проекта Yatube'
    # Получаем все записи
    posts = Post.objects.select_related('author', 'group').all()
    # Показываем столько записей на странице
    paginator = Paginator(posts, COUNT_LAST_POSTS)
    # Из URL извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    context = {
        'home': home,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug=None):
    # Получаем объект модели group, в соответсвии с запросом
    group = get_object_or_404(Group, slug=slug)
    # Шаблон стартовой страницы group_list.html
    template = 'posts/group_list.html'
    # Последние записи из конкретной группы
    posts = group.posts.select_related('author', 'group').all()
    paginator = Paginator(posts, COUNT_LAST_POSTS)
    # Из URL извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    # Получаем объект модели user, в соответсвии с запросом
    author = get_object_or_404(User, username=username)
    template = 'posts/profile.html'
    # Получаем все записи пользователя
    profile_list = Post.objects.select_related('author').filter(
        author__username=username)
    # Считаем записи
    count_posts = profile_list.count()
    # Показываем столько записей на странице
    paginator = Paginator(profile_list, COUNT_LAST_POSTS)
    # Из URL извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    following = (
        request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=author).exists())
    context = {
        'author': author,
        'count_posts': count_posts,
        'page_obj': page_obj,
        'profile_list': profile_list,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    # Получаем пост по его id
    post = get_object_or_404(Post, id=post_id)
    # Считаем кол-во постов автора текущего поста
    count_posts = Post.objects.filter(author_id=post.author).count()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.all().filter(post__id=post_id)
    context = {
        'post': post,
        'count_posts': count_posts,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
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
    # Получите пост
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
    # Подписчик - вошедший юзер
    user = request.user
    # Получаем посты авторов, у которых user - подписчик
    following_list = Post.objects.select_related(
        'author', 'group').filter(
            author__following__user=user)
    # Паджинируем
    paginator = Paginator(following_list, COUNT_LAST_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Задаем шаблон
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Создаёт подписку пользователя на автора постов"""
    # Потенциальный подписчик
    guest = request.user
    # Автор постов
    author = User.objects.get(username=username)
    # Создаём подписку, только не на себя
    if guest != author:
        Follow.objects.get_or_create(
            user=guest,
            author=author
        )
    return redirect('posts:profile_follow', username=author.username)


@login_required
def profile_unfollow(request, username):
    """Отменяет подписку на автора"""
    # Получаем автора
    author = get_object_or_404(User, username=username)
    # Удаляем подписку
    get_object_or_404(Follow, user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)
