# Generated by Django 4.1.5 on 2023-01-17 06:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalCategory',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                (
                    'is_deleted',
                    models.BooleanField(default=False, verbose_name='Удалена'),
                ),
                (
                    'created',
                    models.DateTimeField(
                        auto_now_add=True, verbose_name='Дата создания'
                    ),
                ),
                (
                    'updated',
                    models.DateTimeField(
                        auto_now=True, verbose_name='Дата последнего обновления'
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Пользователь',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
    ]
