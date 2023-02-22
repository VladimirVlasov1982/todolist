import factory
from django.utils import timezone
from pytest_factoryboy import register

from goals.models import BoardParticipant


@register
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'core.User'

    username = factory.Faker('user_name')
    password = factory.Faker('password')
    email = ''

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._get_manager(model_class).create_user(*args, **kwargs)


class DatesFactoryMixin(factory.django.DjangoModelFactory):
    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)

    class Meta:
        abstract = True


@register
class BoardFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')

    class Meta:
        model = 'goals.Board'

    @factory.post_generation
    def with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, user=owner, role=BoardParticipant.Role.owner)


@register
class BoardParticipantFactory(DatesFactoryMixin):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = 'goals.BoardParticipant'


@register
class GoalCategoryFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = 'goals.GoalCategory'


@register
class GoalFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')
    category = factory.SubFactory(GoalCategoryFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = 'goals.Goal'


@register
class GoalCommentFactory(DatesFactoryMixin):
    user = factory.SubFactory(UserFactory)
    goal = factory.SubFactory(GoalFactory)
    text = factory.Faker('text')

    class Meta:
        model = 'goals.GoalComment'
