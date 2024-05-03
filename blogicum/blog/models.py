from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import BaseModel
from blog.constants import LENGTH
from .managers import PublishedPostsManager


User = get_user_model()


class Post(BaseModel):
    title = models.CharField(max_length=LENGTH, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем'
        ' — можно делать отложенные публикации.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )
    image = models.ImageField(verbose_name='Картинка у публикации', blank=True)

    published_objects = PublishedPostsManager()
    objects = models.Manager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"post_id": self.pk})


class Category(BaseModel):
    title = models.CharField(max_length=LENGTH, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL;'
        ' разрешены символы латиницы, цифры, дефис и подчёркивание.')

    class Meta:
        ordering = ('title',)
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(BaseModel):
    name = models.CharField(max_length=LENGTH, verbose_name='Название места')

    class Meta:
        ordering = ('name',)
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Comment(models.Model):
    post = models.ForeignKey(
        Post, verbose_name='Пост', on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE
    )
    text = models.TextField('Комментарий')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('created_at',)
