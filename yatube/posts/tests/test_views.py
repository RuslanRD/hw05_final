from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Это тестовая группа',
        )
        cls.group_wrong = Group.objects.create(
            title='Другая тестовая группа',
            slug='wrong-group',
            description='В этой группе не должно быть постов',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            pub_date='1949-1-1',
            author=cls.user,
            group=cls.group,
        )
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_pages_uses_correct_template(self):
        templates_page_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': reverse('group_posts', args=[self.group.slug]),
            'post.html': reverse(
                'post', args=[self.user.username, self.post.id]
            ),
            'profile.html': reverse('profile', args=[self.user.username]),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        test_text = response.context.get('page')[0].text
        test_author = response.context.get('page')[0].author.username
        test_group = response.context.get('page')[0].group.title
        self.assertEqual(test_text, self.post.text)
        self.assertEqual(test_author, self.user.username)
        self.assertEqual(test_group, self.group.title)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('group_posts', args=[self.group.slug])
        )
        test_group_title = response.context.get('group').title
        test_group_slug = response.context.get('group').slug
        test_group_description = response.context.get('group').description
        self.assertEqual(test_group_title, self.group.title)
        self.assertEqual(test_group_slug, self.group.slug)
        self.assertEqual(test_group_description, self.group.description)

    def test_new_post_form_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for field_name, field_format in form_fields.items():
            with self.subTest(value=field_name):
                form_field = (
                    response.context.get('form').fields.get(field_name)
                )
                self.assertIsInstance(form_field, field_format)

    def test_post_edit_form_correct_context(self):
        response = self.authorized_client.get(
            reverse('post_edit', args=[self.user.username, self.post.id])
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for field_name, field_format in form_fields.items():
            with self.subTest(value=field_name):
                form_field = (
                    response.context.get('form').fields.get(field_name)
                )
                self.assertIsInstance(form_field, field_format)

    def test_user_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', args=[self.user.username])
        )
        test_text = response.context.get('page')[0].text
        test_author = response.context.get('page')[0].author.username
        test_post_count = response.context.get('posts_count')
        self.assertEqual(test_text, self.post.text)
        self.assertEqual(test_author, self.user.username)
        self.assertEqual(test_post_count, self.post.id)

    def test_user_post_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('post', args=[self.user.username, self.post.id])
        )
        test_text = response.context.get('post').text
        test_author = response.context.get('author').username
        self.assertEqual(test_text, self.post.text)
        self.assertEqual(test_author, self.user.username)

    def test_post_in_right_group(self):
        groups_list = {
            'picked_group': reverse('group_posts', args=[self.group.slug]),
            'wrong_group': reverse('group_posts', args=[self.group_wrong.slug])
        }

        for some_group, reverse_name in groups_list.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                posts_in_group = response.context.get('page')
                if some_group == 'picked_group':
                    self.assertIn(self.post, posts_in_group)
                else:
                    self.assertNotIn(self.post, posts_in_group)

    def test_main_page_display_post(self):
        response = self.authorized_client.get(reverse('index'))
        main_page_view = response.context.get('page')
        self.assertIn(self.post, main_page_view)

    def test_page_not_found(self):
        response = self.client.get('/something/')
        self.assertEqual(response.status_code, 404)

    def test_img_on_pages(self):
        cache.clear()
        with open('media/posts/6u4pxh82dhc31.png', 'rb') as img:
            self.authorized_client.post(
                reverse('new_post'),
                data={
                    'author': self.user,
                    'text': self.post.text,
                    'group': self.group.pk,
                    'image': img,
                }
            )

    def test_cache_index(self):
        response = self.authorized_client.get(reverse('index'))
        Post.objects.create(text='Проверка кэша', author=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Проверка кэша')
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        self.assertContains(response, 'Проверка кэша')


class TestCommentsFollow(TestCase):
    def setUp(self):
        self.not_auth_client = Client()
        self.not_auth_user = User.objects.create_user(
            username='commentator'
        )

        self.client_auth_not_following = Client()
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_not_following = User.objects.create_user(
            username='not_following'
        )
        self.user_follower = User.objects.create_user(
            username='follower'
        )
        self.user_following = User.objects.create_user(
            username='following'
        )
        self.client_auth_not_following.force_login(self.user_not_following)
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user_follower,
        )

        self.follow = Follow.objects.create(
            author=self.user_follower,
            user=self.user_following
        )

        self.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=self.user_not_following,
            post=self.post,
        )

    def test_follow_unfollow(self):
        before = Follow.objects.all().count()
        self.client_auth_follower.get(
            reverse(
                'profile_follow',
                kwargs={
                    'username': self.user_following.username,
                },
            )
        )
        after = Follow.objects.all().count()
        self.assertEqual(before + 1, after)
        self.client_auth_follower.get(
            reverse(
                'profile_unfollow',
                kwargs={
                    'username': self.user_following.username,
                },
            )
        )
        after_delete = Follow.objects.all().count()
        self.assertEqual(before, after_delete)

    def test_following_user_see_the_post(self):
        posts_list = {
            'following': reverse('follow_index'),
            'not_following': reverse('follow_index',)
        }

        for some_user, reverse_name in posts_list.items():
            with self.subTest():
                response_following_user = self.client_auth_following.get(
                    reverse_name
                )
                response_not_following_user = (
                    self.client_auth_not_following.get(reverse_name)
                )
                posts_list_of_following_user = (
                    response_following_user.context.get('page')
                )
                posts_list_of_not_folowing_user = (
                    response_not_following_user.context.get('page')
                )
                if some_user == 'following':
                    self.assertIn(
                        self.post,
                        posts_list_of_following_user
                    )
                if some_user == 'not_following':
                    self.assertNotIn(
                        self.post,
                        posts_list_of_not_folowing_user
                    )

    def test_add_comment(self):
        response = self.client_auth_follower.get(
            reverse('post', args=[self.user_follower.username, self.post.id])
        )

        self.assertContains(response, 'Тестовый комментарий')
