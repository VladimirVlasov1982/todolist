import pytest
from django.urls import reverse
from rest_framework import status
from goals.models import GoalComment, BoardParticipant, GoalCategory, Goal
from tests.utils import BaseTestCase


@pytest.mark.django_db
class TestGoalCommentCreate(BaseTestCase):

    @pytest.fixture(autouse=True)
    def setup(self, board_factory, goal_category_factory, goal_factory, user):
        self.board = board_factory.create(with_owner=user)
        self.category: GoalCategory = goal_category_factory.create(board=self.board, user=user)
        self.goal: Goal = goal_factory.create(category=self.category)
        self.participant: BoardParticipant = self.board.participants.last()
        self.url = reverse('goals:comment-create')

    def test_auth_required(self, client, faker):
        response = client.post(self.url, data=faker.pydict(1))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_reader_failed_create_comment(self, auth_client):
        self.participant.role = BoardParticipant.Role.reader
        self.participant.save(update_fields=('role',))
        response = auth_client.post(self.url, data={'text': 'New text', 'goal': self.goal.id})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.writer, BoardParticipant.Role.owner],
        ids=['writer', 'owner']
    )
    def test_success(self, auth_client, user_role):
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))
        response = auth_client.post(self.url, data={
            'text': 'New comment',
            'goal': self.goal.id
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert GoalComment.objects.count() == 1

        new_comment = GoalComment.objects.last()
        assert response.data == {
            'id': new_comment.id,
            'created': self.datetime_to_str(new_comment.created),
            'updated': self.datetime_to_str(new_comment.updated),
            'text': 'New comment',
            'goal': self.goal.id
        }
