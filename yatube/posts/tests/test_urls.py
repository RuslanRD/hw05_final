from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)


User = get_user_model()


class GroupURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок тестовой',
            slug='test-group',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_1 = User.objects.create_user(username="TestUser")
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        self.post_1 = Post.objects.create(
            text='Тестовый текст 2',
            author=self.user_1,
            group=self.group,
        )

    def tests_public_urls(self):
        urls_slugs = {
            '/': 200,
            '/new/': 302,
            f'/group/{self.group.slug}/': 200,
            f'/{self.user_1.username}/': 200,
            f'/{self.user_1.username}/{self.post_1.id}/': 200,
            f'/{self.user_1.username}/{self.post_1.id}/edit/': 302,
        }

        for url, expected_code in urls_slugs.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_code)

    def test_task_list_url_exists_at_desired_location(self):
        urls_slugs = {
            '/new/': 200,
            f'/{self.user_1.username}/{self.post_1.id}/edit/': 302,
            f'/{self.user.username}/{self.post.id}/edit/': 200,
        }
        for url, expected_code in urls_slugs.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_code)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'index.html': '/',
            'new.html': '/new/',
            'group.html': f'/group/{self.group.slug}/',
            'profile.html': f'/{self.user_1.username}/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
