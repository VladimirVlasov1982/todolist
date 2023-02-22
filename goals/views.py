from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant
from goals.permissions import IsOwnerOrReadOnly, BoardPermissions, GoalCategoryPermissions, GoalPermissions, \
    CommentsPermissions
from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, \
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardCreateSerializer, BoardListSerializer, \
    BoardSerializer


class BoardCreateView(generics.CreateAPIView):
    """
    Создает новую доску
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BoardCreateSerializer

    def perform_create(self, serializer):
        """Делаем текущего пользователя владельцем доски"""
        BoardParticipant.objects.create(user=self.request.user, board=serializer.save())


class BoardListView(generics.ListAPIView):
    """
    Возвращает список всех досок.
    Пользователь получает все доски, в которых он является участником или владельцем.
    Удаленные доски не выводятся.
    Есть сортировка по названию.
    """
    model = Board
    permission_classes = (BoardPermissions,)
    serializer_class = BoardListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return Board.objects.filter(participants__user_id=self.request.user.id, is_deleted=False)


class BoardView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление досок.
    При удалении доски удаляются все категории, все цели переводятся в статус архив.
    """
    model = Board
    serializer_class = BoardSerializer
    permission_classes = (BoardPermissions,)

    def get_queryset(self):
        return Board.objects.filter(
            participants__user_id=self.request.user.id,
            is_deleted=False,
        )

    def perform_destroy(self, instance: Board) -> Board:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
        return instance


class GoalCategoryCreateView(generics.CreateAPIView):
    """
    Создает новую категорию.
    Создать категорию может пользователь, который обладает ролью «Владелец» или «Редактор» в данной доске.
    """
    permission_classes = (GoalCategoryPermissions,)
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(generics.ListAPIView):
    """
    Возвращает список всех категорий доски, владельцем или участником которой является текущий пользователь.
    Есть фильтрация по доске.
    """
    model = GoalCategory
    permission_classes = (GoalCategoryPermissions,)
    serializer_class = GoalCategorySerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    filterset_fields = ['board']
    ordering_fields = ['title', 'created']
    ordering = ['title', 'created']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
            is_deleted=False,
            board__participants__user_id=self.request.user.id,
        )


class GoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление категории.
    Редактировать категории можно только обладателям роли «Владелец» или «Редактор»,
    читателю изменять/удалять категории нельзя.
    """
    model = GoalCategory
    permission_classes = (GoalCategoryPermissions,)
    serializer_class = GoalCategorySerializer

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
            is_deleted=False,
            board__participants__user_id=self.request.user.id,
        )

    def perform_destroy(self, instance: GoalCategory) -> GoalCategory:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.goals.update(status=Goal.Status.archived)
        return instance


class GoalCreateView(generics.CreateAPIView):
    """
    Создает новую цель.
    Пользователь может создавать цели только в тех категориях,
    в досках которых он является участником с ролью «Владелец» или «Редактор».
    """
    permission_classes = (GoalPermissions,)
    serializer_class = GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """
    Возвращает список всех целей.
    Пользователю выдаются только те цели, которые находятся в категориях, в досках которых он является участником.
    Есть сортировка по названию.
    """
    model = Goal
    permission_classes = (GoalPermissions,)
    serializer_class = GoalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Goal.objects.filter(
            Q(category__board__participants__user_id=self.request.user.id) & ~Q(status=Goal.Status.archived) & Q(
                category__is_deleted=False)
        )


class GoalView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление целей.
    Пользователь может изменять/удалять цели только в тех категориях,
    в досках которых он является участником с ролью «Владелец» или «Редактор».
    """
    model = Goal
    permission_classes = (GoalPermissions,)
    serializer_class = GoalSerializer

    def get_queryset(self):
        return Goal.objects.filter(
            ~Q(status=Goal.Status.archived) & Q(category__is_deleted=False)
        )

    def perform_destroy(self, instance: Goal) -> Goal:
        with transaction.atomic():
            instance.status = Goal.Status.archived
            instance.save()
        return instance


class GoalCommentCreateView(generics.CreateAPIView):
    """
    Создает комментарий.
    Пользователь может создавать комментарии только к тем целям,
    в досках которых он является участником с ролью «Владелец» или «Редактор».
    """
    permission_classes = (CommentsPermissions, IsOwnerOrReadOnly)
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(generics.ListAPIView):
    """
    Возвращает список комментариев.
    Пользователю выдаются только те комментарии, которые находятся в целях,
    в досках которых он является участником.
    """
    model = GoalComment
    permission_classes = (CommentsPermissions,)
    serializer_class = GoalCommentSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ['goal']
    ordering = ('-created',)

    def get_queryset(self):
        return GoalComment.objects.filter(
            goal__category__board__participants__user_id=self.request.user.id,
        )


class GoalCommentView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление комментария.
    Пользователь не может редактировать/удалять чужие комментарии.
    """
    model = GoalComment
    permission_classes = (CommentsPermissions, IsOwnerOrReadOnly)
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(
            user_id=self.request.user.id,
        )
