import django_filters
from django.db import models
from django_filters import rest_framework
from goals.models import Goal


class GoalDateFilter(rest_framework.FilterSet):
    """
    Фильтр цели
    """

    class Meta:
        model = Goal
        fields = {
            'due_date': ('gte', 'lte'),
            'category': ('exact', 'in'),
            'status': ('exact', 'in'),
            'priority': ('exact', 'in'),
        }
        filter_overrides = {
            models.DateTimeField: {'filter_class': django_filters.IsoDateTimeFilter}
        }
