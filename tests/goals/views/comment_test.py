import pytest
from django.urls import reverse
from rest_framework import status

from core.serializers import ProfileSerializer
from goals.models import GoalComment, BoardParticipant, GoalCategory, Goal
from tests.utils import BaseTestCase


@pytest.fixture
def another_user(user_factory):
    return user_factory.create()


@pytest.mark.django_db
class TestGoalCommentRetrieve(BaseTestCase):
    @pytest.fixture(autouse=True)
    def setup(self, board_factory, goal_category_factory, goal_factory,
              goal_comment_factory, user):
        self.board = board_factory.create(with_owner=user)
        self.category: GoalCategory = goal_category_factory.create(board=self.board, user=user)
        self.goal: Goal = goal_factory.create(category=self.category, user=user)
        self.comment: GoalComment = goal_comment_factory.create(goal=self.goal, user=user)
        self.url = reverse('goals:comment-view', args=[self.comment.pk])

    def test_auth_required(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client, user):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': self.comment.pk,
            'user': ProfileSerializer(user).data,
            'created': self.datetime_to_str(self.comment.created),
            'updated': self.datetime_to_str(self.comment.updated),
            'text': self.comment.text,
            'goal': self.goal.pk
        }

    def test_comment_not_found(self, client, another_user):
        client.force_login(another_user)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestGoalCommentDestroy(BaseTestCase):

    @pytest.fixture(autouse=True)
    def setup(self, board_factory, goal_category_factory, goal_comment_factory, goal_factory, user):
        self.board = board_factory.create(with_owner=user)
        self.category: GoalCategory = goal_category_factory.create(board=self.board, user=user)
        self.goal: Goal = goal_factory.create(category=self.category, user=user)
        self.comment: GoalComment = goal_comment_factory.create(goal=self.goal, user=user)
        self.url = reverse('goals:comment-view', args=[self.comment.pk])

    def test_auth_required(self, client):
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client):
        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not GoalComment.objects.count()


@pytest.mark.django_db
class TestGoalCommentUpdate(BaseTestCase):

    @pytest.fixture(autouse=True)
    def setup(self, board_factory, goal_category_factory, goal_factory, goal_comment_factory, user):
        self.board = board_factory.create(with_owner=user)
        self.category: GoalCategory = goal_category_factory.create(board=self.board, user=user)
        self.goal: Goal = goal_factory.create(category=self.category, user=user)
        self.comment: GoalComment = goal_comment_factory.create(goal=self.goal, user=user)
        self.participant: BoardParticipant = self.board.participants.last()
        self.url = reverse('goals:comment-view', args=[self.comment.pk])

    @pytest.mark.parametrize('method', ['put', 'patch'])
    def test_auth_required(self, client, method):
        response = getattr(client, method)(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client, faker):
        new_text = faker.sentence()
        response = auth_client.patch(self.url, {'text': new_text})
        assert response.status_code == status.HTTP_200_OK

        self.comment.refresh_from_db(fields=('text',))
        assert self.comment.text == new_text
