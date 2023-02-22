import pytest
from django.urls import reverse
from rest_framework import status
from goals.models import BoardParticipant, Goal, GoalCategory
from tests.utils import BaseTestCase


@pytest.fixture
def another_user(user_factory):
    return user_factory.create()


@pytest.mark.django_db
class TestGoalCategoryRetrieve(BaseTestCase):
    @pytest.fixture(autouse=True)
    def setup(self, goal_category_factory, user, board_factory):
        self.board = board_factory.create(with_owner=user)
        self.category = goal_category_factory.create(user=user, board=self.board)
        self.url = reverse('goals:category-view', args=[self.category.id])

    def test_auth_required(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client, user):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': self.category.id,
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            },
            'created': self.datetime_to_str(self.category.created),
            'updated': self.datetime_to_str(self.category.updated),
            'title': self.category.title,
            'is_deleted': False,
            'board': self.board.id
        }

    def test_category_not_found(self, client, another_user):
        client.force_login(another_user)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestGoalCategoryDestroy(BaseTestCase):

    @pytest.fixture(autouse=True)
    def setup(self, goal_category_factory, board_factory, goal_factory, user):
        self.board = board_factory.create(with_owner=user)
        self.category: GoalCategory = goal_category_factory.create(board=self.board, user=user)
        self.url = reverse('goals:category-view', args=[self.category.pk])
        self.goal: Goal = goal_factory.create(category=self.category, user=user)
        self.participant: BoardParticipant = self.board.participants.last()

    def test_auth_required(self, client):
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_the_reader_cannot_delete_category(self, auth_client):
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

        self.category.refresh_from_db(fields=('is_deleted',))
        self.goal.refresh_from_db(fields=('status',))
        assert self.category.is_deleted
        assert self.goal.status == Goal.Status.archived


@pytest.mark.django_db
class TestGoalCategoryUpdate(BaseTestCase):

    @pytest.fixture(autouse=True)
    def setup(self, goal_category_factory, board_factory, user):
        self.board = board_factory.create(with_owner=user)
        self.category: GoalCategory = goal_category_factory.create(board=self.board, user=user)
        self.participant: BoardParticipant = self.board.participants.last()
        self.url = reverse('goals:category-view', args=[self.category.pk])

    @pytest.mark.parametrize('method', ['put', 'patch'])
    def test_auth_required(self, client, method):
        response = getattr(client, method)(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_reader_failed_to_update_category(self, auth_client):
        self.participant.role = BoardParticipant.Role.reader
        self.participant.save(update_fields=('role',))

        response = auth_client.patch(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.writer, BoardParticipant.Role.owner],
        ids=('writer', 'owner')
    )
    def test_update_category(self, auth_client, user_role, faker):
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))

        new_title = faker.sentence()
        response = auth_client.patch(self.url, {'title': new_title})
        assert response.status_code == status.HTTP_200_OK

        self.category.refresh_from_db(fields=('title',))
        assert self.category.title == new_title
