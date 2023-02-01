from django.db import models

from core.models import User


class TgUser(models.Model):
    tg_id = models.IntegerField()
    username = models.CharField(max_length=255)
    verification_code = models.CharField(min_length=1, max_length=255)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь', related_name='telegram_user')

    objects = models.Manager()

    def __str__(self):
        return self.user
