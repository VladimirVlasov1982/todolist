import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Goal
from tests.utils import BaseTestCase


@pytest.mark.django_db
class TestGoalList(BaseTestCase):
    url = reverse('goals:goal-list')

    def test_auth_required(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_goal_list(self, auth_client, goal_factory):
        goal_factory.create_batch(10)
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(Goal.objects.all()) == 10
