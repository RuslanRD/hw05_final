from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Группа для тестирования',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group.id,
                text='Тестовый текст').exists()
        )

    def test_post_edit(self):
        form_data = {
            'text': 'Отредактированный тестовый текст',
            'group': PostFormTests.group.id
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=[self.user.username, self.post.id]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('post', args=[self.user.username, self.post.id])
        )
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group.id,
                text='Отредактированный тестовый текст').exists()
        )
