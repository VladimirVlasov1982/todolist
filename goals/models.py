from django.db import models

from core.models import User


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


class Goal(DatesModelMixin):
    """
    Модель цели
    """
    title = models.CharField(verbose_name='Название', max_length=255)
    description = models.TextField(verbose_name='Описание')
    category = models.ForeignKey(GoalCategory, on_delete=models.PROTECT, verbose_name='Категория')
    status = models.PositiveSmallIntegerField(verbose_name='Статус', choices=Status.choices, default=Status.to_do)
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет', choices=Priority.choices,
                                                default=Priority.medium)
    due_date = models.DateTimeField(verbose_name='Срок выполнения')

    objects = models.Manager()

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'
