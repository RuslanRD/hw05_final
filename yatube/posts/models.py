from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        max_length=200,
        help_text='Дай название группе',
    )
    slug = models.SlugField(
        'Уникальный адрес',
        unique=True,
        help_text='Используй, пожалуйста, уникальное имя для slug',
    )
    description = models.TextField(
        'Описание группы',
        help_text='Опиши тематику группы',
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст автора',
        help_text='Напиши свой пост здесь',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Отображается дата публикации поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Указывается автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Указывается группа'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
        verbose_name='Комментарий к посту',
        help_text='Добавь комментарий к посту'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Указывается автор комментария'
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Комментарий к посту',
        help_text='Пиши текст комментария здесь'
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
        help_text='Отображается дата публикации комментария',
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        unique_together = ['user', 'author']

    def __str__(self):
        return f'user: {self.user.username} author: {self.author.username}'
