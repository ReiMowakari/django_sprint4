from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class BaseModel(models.Model):
    """Абстрактная модель для исключения повторений."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    """Тематическая категория."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL;'
            ' разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    """Географическая метка."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):
    """Публикации."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем'
            ' — можно делать отложенные публикации.'
        )
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts',
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts',
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts',
    )

    image = models.ImageField('Изображения',
                              upload_to='posts_images',
                              blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Модель для комментариев."""
    text = models.TextField(
        'Оставить комментарий'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
    )
    created_at = models.DateTimeField(
        'Дата и время создания',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
