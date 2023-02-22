from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from core.models import User
from core.serializers import ProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class BoardCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания доски
    """

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')


class BoardParticipantSerializer(serializers.ModelSerializer):
    """
    Сериализатор участников доски
    """
    role = serializers.ChoiceField(
        required=True,
        choices=BoardParticipant.Role.choices[1:],
    )
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    def validate(self, attrs):
        if attrs['user'] == self.context['request'].user and attrs['role'] != BoardParticipant.Role.owner:
            raise PermissionDenied('Не удалось обновить роль владельца')
        return attrs

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardListSerializer(serializers.ModelSerializer):
    """
    Сериализатор списка досок
    """

    class Meta:
        model = Board
        fields = '__all__'


class BoardSerializer(serializers.ModelSerializer):
    """
    Сериализатор доски
    """
    participants = BoardParticipantSerializer(many=True)

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')

    def update(self, instance: Board, validated_data: dict) -> Board:
        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=self.context['request'].user).delete()
            BoardParticipant.objects.bulk_create([
                BoardParticipant(
                    user=participant['user'],
                    role=participant['role'],
                    board=instance
                )
                for participant in validated_data.pop('participants', [])
            ])
            if title := validated_data.get('title'):
                instance.title = title
                instance.save()
        return instance


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания категории
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted',)

    def validate_board(self, value: Board) -> Board:
        if value.is_deleted:
            raise serializers.ValidationError('Доска удалена')
        if not BoardParticipant.objects.filter(
                board=value,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id,
        ):
            raise PermissionDenied('Вы должны быть владельцем или редактором доски')
        return value


class GoalCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор категории
    """
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'board')


class GoalCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания цели
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        if not BoardParticipant.objects.filter(
                board=value.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id
        ):
            raise PermissionDenied('Вы должны быть владельцем или редактором доски')
        return value


class GoalSerializer(serializers.ModelSerializer):
    """
    Сериализатор цели
    """

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания комментария
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_goal(self, value: Goal) -> Goal:
        if not BoardParticipant.objects.filter(
                board=value.category.board.pk,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id,
        ):
            raise PermissionDenied('Недостаточно прав')
        return value


class GoalCommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор комментария
    """
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')
