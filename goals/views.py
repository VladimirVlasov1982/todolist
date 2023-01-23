from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment
from goals.permissions import IsOwnerOrReadOnly
from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, \
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer


class GoalCategoryCreateView(generics.CreateAPIView):
    """
    Создает новую категорию
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(generics.ListAPIView):
    """
    Возвращает список всех категорий
    """
    model = GoalCategory
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalCategorySerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    ordering_fields = ['title', 'created']
    ordering = ['title', 'created']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.select_related('user').filter(
            user_id=self.request.user.id,
            is_deleted=False,
        )


class GoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление категории
    """
    model = GoalCategory
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalCategorySerializer

    def get_queryset(self):
        return GoalCategory.objects.select_related('user').filter(
            user_id=self.request.user.id,
            is_deleted=False,
        )

    def perform_destroy(self, instance: GoalCategory) -> GoalCategory:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.goals.update(status=Goal.Status.archived)
        return instance


class GoalCreateView(generics.CreateAPIView):
    """
    Создает новую цель
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """
    Возвращает список всех целей.
    """
    model = Goal
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Goal.objects.filter(
            Q(user_id=self.request.user.id) & ~Q(status=Goal.Status.archived) & Q(category__is_deleted=False)
        )


class GoalView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление целей
    """
    model = Goal
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()

    def get_queryset(self):
        return Goal.objects.filter(
            ~Q(status=Goal.Status.archived) & Q(category__is_deleted=False)
        )


class GoalCommentCreateView(generics.CreateAPIView):
    """
    Создает комментарий
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(generics.ListAPIView):
    """
    Возвращает список комментариев
    """
    model = GoalComment
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GoalCommentSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ['goal']
    ordering = ('-created',)

    def get_queryset(self):
        return GoalComment.objects.filter(
            user_id=self.request.user.id,
        )


class GoalCommentView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление комментария
    """
    model = GoalComment
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(
            user_id=self.request.user.id,
        )
