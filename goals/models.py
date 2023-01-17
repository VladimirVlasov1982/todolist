from django.db import models

from core.models import User


class GoalCategory(models.Model):
    """
    Модель категории цели
    """
    title = models.CharField(max_length=255, verbose_name='Название')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')
    is_deleted = models.BooleanField(default=False, verbose_name='Удалена')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
