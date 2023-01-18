from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal
from goals.permissions import IsOwnerCategoryOrNot, IsOwnerGoalOrNot
from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, GoalSerializer


class GoalCategoryCreateView(generics.CreateAPIView):
    """
    Создать новую категорию цели
    """
    model = GoalCategory
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(generics.ListAPIView):
    """
    Список всех категорий цели
    """
    model = GoalCategory
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    ordering_fields = ('title', 'created')
    ordering = ('title',)
    search_fields = ('title',)

    def get_queryset(self):
        return GoalCategory.objects.filter(
            user=self.request.user,
            is_deleted=False,
        )


class GoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление категории цели
    """
    model = GoalCategory
    permission_classes = (permissions.IsAuthenticated, IsOwnerCategoryOrNot)
    serializer_class = GoalCategorySerializer

    def get_queryset(self):
        return GoalCategory.objects.filter(
            user=self.request.user,
            is_deleted=False,
        )

    def perform_destroy(self, instance: GoalCategory) -> GoalCategory:
        instance.is_deleted = True
        instance.save()
        return instance


class GoalCreateView(generics.CreateAPIView):
    """
    Создать новую цель
    """
    model = Goal
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """
    Список всех целей.
    """
    model = Goal
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filterset_class = GoalDateFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ('title', 'created',)
    ordering = ('title',)
    search_fields = ('title', 'description')

    def get_queryset(self):
        return Goal.objects.filter()


class GoalView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление целей
    """
    model = Goal
    permission_classes = (permissions.IsAuthenticated, IsOwnerGoalOrNot)
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()

    def perform_destroy(self, instance):
        instance.status = 4
        instance.save()
        return instance
