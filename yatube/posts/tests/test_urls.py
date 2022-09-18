from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Pushkin')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test_slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        super().setUp()
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаём экземпляр клиента. Авторизован.
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем доступы для неавторизованного
    def test_pages_for_guest(self):
        """Страницы: главная, посты группы, профайл пользователя, детали поста
        доступны неавторизованному пользователю
        """
        user_for_test = reverse(
            'posts:profile', kwargs={'username': self.user.username})
        post_for_test = reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        group_for_test = reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        guests_pages = [
            '/',
            group_for_test,
            user_for_test,
            post_for_test,
        ]
        for page in guests_pages:
            with self.subTest(page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступы для авторизованного пользователя
    def test_post_create(self):
        """Форма создания нового поста доступна
        авторизованному пользователю
        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """ Форма редактирования своего поста доступна автору
        """
        response = self.authorized_client.get(
            reverse('posts:post_edit', args={self.post.pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного пользователя
    def test_create_post_url_redirect_anonymous_on_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_edit_post_url_redirect_anonymous_on_login(self):
        """Страница с формой редактирования поста
        перенаправит анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}), follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/')

    # Проверяем правильность вызова шаблонов
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', args={self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', args={self.post.pk}):
                'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_non_existent_page(self):
        response = self.guest_client.get('/no-name/')
        template = 'core/404.html'
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, template)

    def test_error_403(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post("/")
        self.assertContains(response, "Test template for CSRF failure", status_code=403)
