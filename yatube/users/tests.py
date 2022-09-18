from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostsURLTests(TestCase):
    def setUp(self) -> None:
        super().setUp()
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Shekspir')
        # Создаём экземпляр клиента. Авторизован.
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем доступы для неавторизованного
    def test_pages_for_guest(self):
        """Страницы: login, logout, signup
        доступны неавторизованному пользователю
        """
        guests_pages = [
            reverse('users:login'),
            reverse('users:logout'),
            reverse('users:signup'),
            reverse('password_reset'),
            reverse('password_reset_done'),
        ]
        for page in guests_pages:
            with self.subTest(page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступы для авторизованного
    def test_pages_for_user(self):
        """Страницы: смены, восстановления пароля
        доступны неавторизованному пользователю
        """
        users_pages = [
            reverse('password_change'),
            reverse('password_change_done'),
        ]
        for page in users_pages:
            with self.subTest(page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного
    def test_password_change_redirect_anonymous_on_login(self):
        """Страница по адресу /auth/password_change/
        перенаправит анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(
            reverse('password_change'), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/auth/password_change/')

    def test_password_change_done_redirect_anonymous_on_login(self):
        """Страница по адресу /auth/password_change/done/
        перенаправит анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(
            reverse('password_change_done'), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/auth/password_change/done/')
