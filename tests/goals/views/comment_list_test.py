import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import GoalComment
from tests.utils import BaseTestCase


@pytest.mark.django_db
class TestGoalCommentList(BaseTestCase):
    url = reverse('goals:comment-list')

    def test_auth_required(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client, goal_comment_factory):
        goal_comment_factory.create_batch(10)
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(GoalComment.objects.all()) == 10
