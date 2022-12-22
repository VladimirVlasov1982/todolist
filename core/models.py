from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Модель пользователя
    """

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
