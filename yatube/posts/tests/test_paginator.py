from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test-description')

        Post.objects.create(
            text='Тестовый текст 1',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 2',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 3',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 4',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 5',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 6',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 7',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 8',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 9',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 10',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 11',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 12',
            author=cls.user,
            group=cls.group
        )

        Post.objects.create(
            text='Тестовый текст 13',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_containse_ten_records(self):
        counts_of_posts = {
            reverse('index'): 10,
            reverse('group_posts', args=[self.group.slug]): 10,
            reverse('profile', args=[self.user]): 10,
        }

        for reverse_name, counts in counts_of_posts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context.get('page').object_list), counts
                )

    def test_second_page_containse_three_records(self):
        counts_of_posts = {
            reverse('index'): 3,
            reverse('group_posts', args=[self.group.slug]): 3,
            reverse('profile', args=[self.user.username]): 3,
        }

        for reverse_name, counts in counts_of_posts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context.get('page').object_list), counts
                )
