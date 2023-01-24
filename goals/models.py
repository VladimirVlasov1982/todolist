from django.db import models

from core.models import User


class DatesModelMixin(models.Model):
    """
    Миксин для моделей с полями даты
    """
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')

    class Meta:
        abstract = True


class GoalCategory(DatesModelMixin):
    """
    Модель категории цели
    """
    title = models.CharField(max_length=255, verbose_name='Название')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')
    is_deleted = models.BooleanField(default=False, verbose_name='Удалена')

    objects = models.Manager()

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Goal(DatesModelMixin):
    """
    Модель цели
    """

    class Status(models.IntegerChoices):
        """
        Статус
        """
        to_do = 1, 'К выполнению'
        in_progress = 2, 'В работе'
        done = 3, 'Выполнено'
        archived = 4, 'Архив'

    class Priority(models.IntegerChoices):
        """
        Приоритет
        """
        low = 1, 'Низкий'
        medium = 2, 'Средний'
        high = 3, 'Высокий'
        critical = 4, 'Критический'

    title = models.CharField(verbose_name='Название', max_length=255)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    category = models.ForeignKey(GoalCategory, on_delete=models.PROTECT, verbose_name='Категория', related_name='goals')
    status = models.PositiveSmallIntegerField(
        verbose_name='Статус',
        choices=Status.choices,
        default=Status.to_do
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name='Приоритет',
        choices=Priority.choices,
        default=Priority.medium
    )
    due_date = models.DateField(verbose_name='Срок выполнения', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Автор', related_name='goals')

    objects = models.Manager()

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    def __str__(self):
        return self.title


class GoalComment(DatesModelMixin):
    """
    Модель комментариев
    """
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, verbose_name='Цель', related_name='comments')
    text = models.TextField(verbose_name='Комментарий')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Автор', related_name='comments')

    objects = models.Manager()

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
