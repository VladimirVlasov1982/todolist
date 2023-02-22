import pytest
from django.urls import reverse
from rest_framework import status
from goals.models import BoardParticipant, Goal, GoalCategory
from tests.utils import BaseTestCase


@pytest.fixture
def another_user(user_factory):
    return user_factory.create()


@pytest.mark.django_db
class TestGoalRetrieve(BaseTestCase):
    @pytest.fixture(autouse=True)
    def setup(self, board_factory, goal_category_factory, goal_factory, user):
        self.board = board_factory.create(with_owner=user)
        self.category: GoalCategory = goal_category_factory.create(user=user, board=self.board)
        self.goal: Goal = goal_factory.create(user=user, category=self.category)
        self.url = reverse('goals:goal-view', args=[self.goal.pk])

    def test_auth_required(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client, user):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': self.goal.pk,
            'title': self.goal.title,
            'created': self.datetime_to_str(self.goal.created),
            'updated': self.datetime_to_str(self.goal.updated),
            'description': self.goal.description,
            'status': self.goal.status,
            'priority': self.goal.priority,
            'due_date': self.goal.due_date,
            'category': self.category.pk,
            'user': user.id
        }

    def test_goal_not_found(self, auth_client):
        self.url = reverse('goals:goal-view', args=[2])
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDestroyGoal(BaseTestCase):

    @pytest.fixture(autouse=True)
    def setup(self, board_factory, goal_category_factory, goal_factory, user):
        self.board = board_factory.create(with_owner=user)
        self.category: GoalCategory = goal_category_factory.create(board=self.board, user=user)
        self.goal: Goal = goal_factory.create(category=self.category, user=user)
        self.url = reverse('goals:goal-view', args=[self.goal.pk])
        self.participant: BoardParticipant = self.board.participants.last()

    def test_auth_required(self, client):
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_the_reader_cannot_delete_goal(self, auth_client):
        self.participant.role = BoardParticipant.Role.reader
        self.participant.save(update_fields=('role',))

        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.writer, BoardParticipant.Role.owner],
        ids=['writer', 'owner']
    )
    def test_success(self, auth_client, user_role):
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))

        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        self.goal.refresh_from_db(fields=('status',))
        assert self.goal.status == Goal.Status.archived


@pytest.mark.django_db
class TestUpdateGoal(BaseTestCase):

    @pytest.fixture(autouse=True)
    def setup(self, board_factory, goal_category_factory, goal_factory, user):
        self.board = board_factory.create(with_owner=user)
        self.category: GoalCategory = goal_category_factory.create(board=self.board, user=user)
        self.goal: Goal = goal_factory.create(category=self.category, user=user)
        self.participant: BoardParticipant = self.board.participants.last()
        self.url = reverse('goals:goal-view', args=[self.goal.pk])

    @pytest.mark.parametrize('method', ['put', 'patch'])
    def test_auth_required(self, client, method):
        response = getattr(client, method)(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_reader_failed_to_update_goal(self, auth_client):
        self.participant.role = BoardParticipant.Role.reader
        self.participant.save(update_fields=('role',))

        response = auth_client.patch(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.writer, BoardParticipant.Role.owner],
        ids=('writer', 'owner')
    )
    def test_update_goal(self, auth_client, user_role, faker, goal_category_factory):
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))

        new_title = faker.sentence()
        new_description = faker.sentence()
        new_category = goal_category_factory.create()

        response = auth_client.patch(self.url, {
            'title': new_title,
            'description': new_description,
            'category': new_category.id,
        })
        assert response.status_code == status.HTTP_200_OK

        self.goal.refresh_from_db(fields=('title', 'description', 'category'))
        assert self.goal.title == new_title
        assert self.goal.description == new_description
        assert self.goal.category.id == new_category.id
