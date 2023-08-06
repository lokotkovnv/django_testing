from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability(self):
        urls = (
            '/',
            '/auth/login/',
            '/auth/logout/',
            '/auth/signup/',
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_authenticated_users(self):
        user = self.author
        urls = (
            '/notes/',
            '/done/',
            '/add/',
        )
        self.client.force_login(user)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        url_patterns = (
            '/note/{}/',
            '/edit/{}/',
            '/delete/{}/',
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for pattern in url_patterns:
                with self.subTest(user=user, pattern=pattern):
                    url = pattern.format(self.note.slug)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        login_url = '/auth/login/'
        url_patterns = (
            ('/note/{}/', (self.note.slug,)),
            ('/edit/{}/', (self.note.slug,)),
            ('/delete/{}/', (self.note.slug,)),
            ('/add/', None),
            ('/done/', None),
            ('/notes/', None),
        )
        for pattern, args in url_patterns:
            with self.subTest(pattern=pattern):
                if args:
                    url = pattern.format(*args)
                else:
                    url = pattern
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
