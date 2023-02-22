import pytest
from django.urls import reverse
from rest_framework import status
from goals.models import GoalCategory
from tests.utils import BaseTestCase


@pytest.mark.django_db
class TestGoalCategoryList(BaseTestCase):
    url = reverse('goals:category-list')

    def test_auth_required(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_category_list(self, auth_client, goal_category_factory):
        goal_category_factory.create_batch(10)
        response = auth_client.get(self.url, {'limit': 3})

        assert response.status_code == status.HTTP_200_OK
        assert len(GoalCategory.objects.all()) == 10
