from django.db import models

from core.models import User


class TgUser(models.Model):
    chat_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь', related_name='telegram_user')

    objects = models.Manager()

    def __str__(self):
        return self.user
