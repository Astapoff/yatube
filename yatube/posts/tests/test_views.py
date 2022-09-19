import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow

User = get_user_model()

COUNT_NEW_POSTS = 13
COUNT_POSTS_ON_PAGE = 10

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Pushkin')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test_slug'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', args={self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', args={self.post.id}):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        content = response.context['page_obj']
        for post in content:
            self.assertEqual(post, self.post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        content = response.context.get('page_obj')
        for post in content:
            self.assertEqual(post, self.post)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context['post'].text, 'Тестовый текст')
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author}))
        content = response.context.get('page_obj')
        for post in content:
            self.assertEqual(post, self.post)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='new_post',
            author=self.user,
        )
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)


class TestPaginatorPages(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='Автор')
        cls.group = Group.objects.create(
            title='Название',
            slug='address',
            description='Описание',
        )
        cls.post_list = []
        for i in range(COUNT_NEW_POSTS):
            cls.post_list.append(Post(
                author=cls.author,
                text='Текст',
                group=cls.group,
            ))
        cls.post = Post.objects.bulk_create(cls.post_list)

    def setUp(self):
        self.auth_author = Client()
        self.auth_author.force_login(self.author)

    def test_paginator_for_pages(self):
        pages = {
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            ),
        }
        for page in pages:
            with self.subTest(page=page):
                response_page_one = self.auth_author.get(page)
                response_page_two = self.auth_author.get(
                    page + '?page=2'
                )
                context_for_first = response_page_one.context.get(
                    'page_obj'
                )
                context_for_second = len(
                    response_page_two.context.get('page_obj')
                )
                post_for_second = len(self.post) - COUNT_POSTS_ON_PAGE
                self.assertIsInstance(context_for_first, Page)
                self.assertEqual(len(context_for_first), COUNT_POSTS_ON_PAGE)
                self.assertEqual(context_for_second, post_for_second)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.following = User.objects.create_user(username='following')
        cls.anonym = User.objects.create_user(username='anonym')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.following,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        self.follower_client = Client()
        self.following_client = Client()
        self.follower_client.force_login(self.follower)
        self.following_client.force_login(self.following)

    def test_profile_follow(self):
        """Проверка создания подписки на автора"""
        follow = Follow.objects.all().count()
        self.follower_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.following.username}))
        self.assertEqual(Follow.objects.all().count(), follow + 1)

    def test_profile_unfollow(self):
        """Проверка отписки (удаления подписки)"""
        self.follower_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.following.username}))
        self.follower_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_follow(self):
        """Проверка отображения у подписчика нового поста автора"""
        Follow.objects.create(
            user=self.follower,
            author=self.following,
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertContains(response, self.post.text)

    def test_anonymous_follow(self):
        """У не подписанного юзера не отображается пост автора"""
        test_client = Client()
        test_client.force_login(self.anonym)
        Follow.objects.create(
            user=self.follower,
            author=self.following,
        )
        response = test_client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, 'Тестовый текст')
