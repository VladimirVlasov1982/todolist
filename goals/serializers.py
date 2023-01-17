from rest_framework import serializers

from core.serializers import ProfileSerializer
from goals.models import GoalCategory


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
