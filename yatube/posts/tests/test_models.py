# deals/tests/tests_models.py
from django.test import TestCase
from posts.models import Group, Post, User


class GroupModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-group',
            description='Тестовое описание'
        )

    def test_verbose_name_group(self):
        group = GroupModelsTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальный адрес',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text_group(self):
        group = GroupModelsTest.group
        field_help_texts = {
            'title': 'Дай название группе',
            'slug': 'Используй, пожалуйста, уникальное имя для slug',
            'description': 'Опиши тематику группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_title_max_length_not_exceed(self):
        group = GroupModelsTest.group
        max_length_title = group._meta.get_field('title').max_length
        length_title = len(group.title)
        self.assertGreaterEqual(max_length_title, length_title)

    def test_object_name_is_title_field_group(self):
        group = GroupModelsTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class PostModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='01.04.2021',
            author=User.objects.create(username='TestAuthor'),
            group=Group.objects.create(title='Тестовая группа'),
        )

    def test_verbose_name_post(self):
        post = PostModelsTest.post
        field_verboses = {
            'text': 'Текст автора',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        post = PostModelsTest.post
        field_help_texts = {
            'text': 'Напиши свой пост здесь',
            'pub_date': 'Отображается дата публикации поста',
            'author': 'Указывается автор',
            'group': 'Указывается группа',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field_post(self):
        post = PostModelsTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))
