import pytest
from django.urls import reverse
from rest_framework import status
from goals.models import Board, BoardParticipant
from tests.utils import BaseTestCase


@pytest.mark.django_db
class TestBoardCreate(BaseTestCase):
    url = reverse('goals:board-create')

    def test_auth_required(self, client, faker):
        response = client.post(self.url, data=faker.pydict(1))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client, settings):
        response = auth_client.post(self.url, data={'title': 'New Board'})
        assert response.status_code == status.HTTP_201_CREATED
        new_board = Board.objects.last()
        expected_response = {
            'id': new_board.id,
            'title': 'New Board',
            'created': self.datetime_to_str(new_board.created),
            'updated': self.datetime_to_str(new_board.updated),
            'is_deleted': False
        }
        assert response.data == expected_response

    def test_created_board_participant(self, auth_client, user, faker):
        response = auth_client.post(self.url, data={
            'title': faker.sentence(),
        })
        assert response.status_code == status.HTTP_201_CREATED
        new_board = Board.objects.last()
        participants = new_board.participants.all()
        assert len(participants) == 1
        assert participants[0].user == user
        assert participants[0].role == BoardParticipant.Role.owner

    def test_failed_to_create_deleted_board(self, auth_client, faker):
        response = auth_client.post(self.url, data={
            'title': faker.sentence(),
            'is_deleted': True,
        })
        assert response.status_code == status.HTTP_201_CREATED
        new_board = Board.objects.last()
        assert not new_board.is_deleted
