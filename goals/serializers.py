from rest_framework import serializers

from core.serializers import ProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания категории цели
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ('id', 'created', 'updated', 'user',)
        fields = '__all__'


class GoalCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор категории цели
    """
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user',)


class GoalCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания цели
    """

    class Meta:
        model = Goal
        read_only_fields = ('id', 'created', 'updated',)
        fields = '__all__'

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        if value.is_deleted:
            raise serializers.ValidationError('Категория удалена')
        if value.user != self.context['request'].user:
            raise serializers.ValidationError('Не владелец категории')
        return value


class GoalSerializer(serializers.ModelSerializer):
    """
    Сериализатор цели
    """

    class Meta:
        model = Goal
        fields = '__all__'


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания комментария цели
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    goal = serializers.PrimaryKeyRelatedField(queryset=Goal.objects.all())

    class Meta:
        model = GoalComment
        read_only_fields = ('id', 'created', 'updated', 'user',)
        fields = '__all__'


class GoalCommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор комментария цели
    """
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')
