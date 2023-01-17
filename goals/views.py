from rest_framework import generics, permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.models import GoalCategory
from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer


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
    permission_classes = (permissions.IsAuthenticated,)
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
