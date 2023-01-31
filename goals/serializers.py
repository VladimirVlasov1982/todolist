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
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')

    def create(self, validated_data):
        user = validated_data.pop('user')
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(user=user, board=board, role=BoardParticipant.Role.owner)
        return board


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
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

    def update(self, instance, validated_data):
        owner = validated_data.pop('user')
        new_participants = validated_data.pop('participants')
        new_by_id = {part['user'].id: part for part in new_participants}

        old_participants = instance.participants.exclude(user=owner)
        with transaction.atomic():
            for old_participant in old_participants:
                if old_participant.user_id not in new_by_id:
                    old_participant.delete()
                else:
                    if old_participant.role != new_by_id[old_participant.user_id]['role']:
                        old_participant.role = new_by_id[old_participant.user_id]['role']
                        old_participant.save()
                    new_by_id.pop(old_participant.user_id)
            for new_part in new_by_id.values():
                BoardParticipant.objects.create(
                    user=new_part['user'],
                    board=instance,
                    role=new_part['role'],
                )
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

    def validate_goal(self, value: Goal):
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
