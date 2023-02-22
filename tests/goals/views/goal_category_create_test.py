import pytest
from django.urls import reverse
from goals.models import GoalCategory
from tests.utils import BaseTestCase
from rest_framework import status


@pytest.mark.django_db
class TestGoalCategoryCreate(BaseTestCase):
    url = reverse('goals:category-create')

    def test_auth_required(self, client, faker):
        response = client.post(self.url, data=faker.pydict(1))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client, settings, board_factory, user):
        board = board_factory.create(with_owner=user)
        response = auth_client.post(self.url, data={
            'title': 'New category',
            'board': board.pk
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert GoalCategory.objects.count() == 1

        new_category = GoalCategory.objects.last()
        assert response.data == {
            'id': new_category.id,
            'title': 'New category',
            'created': self.datetime_to_str(new_category.created),
            'updated': self.datetime_to_str(new_category.updated),
            'is_deleted': False,
            'board': board.pk
        }
