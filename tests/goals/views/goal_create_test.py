import pytest
from django.urls import reverse
from rest_framework import status
from goals.models import Goal
from tests.utils import BaseTestCase


@pytest.mark.django_db
class TestGoalCreate(BaseTestCase):
    url = reverse('goals:goal-create')

    def test_auth_required(self, client, faker):
        response = client.post(self.url, data=faker.pydict(1))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client, goal_category_factory, board_factory, user):
        board = board_factory.create(with_owner=user)
        category = goal_category_factory.create(user=user, board=board)
        response = auth_client.post(self.url, data={
            'title': 'New goal',
            'category': category.pk
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert Goal.objects.count() == 1

        new_goal = Goal.objects.last()
        assert response.data == {
            'id': new_goal.id,
            'category': category.pk,
            'title': 'New goal',
            'created': self.datetime_to_str(new_goal.created),
            'updated': self.datetime_to_str(new_goal.updated),
            'description': new_goal.description,
            'due_date': new_goal.due_date,
            'status': new_goal.status,
            'priority': new_goal.priority
        }
