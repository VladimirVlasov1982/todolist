import pytest
from django.urls import reverse
from rest_framework import status
from core.models import User
from tests.utils import BaseTestCase


@pytest.mark.django_db
class TestLogin(BaseTestCase):
    url = reverse('core:login')

    def test_user_access(self, client, user_factory, faker):
        password: str = faker.password()
        user: User = user_factory.create(password=password)
        expected_response = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
        }
        data = {
            'username': user.username,
            'password': password
        }
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_response

    def test_user_not_found(self, client, user_factory, faker):
        user = user_factory.build()
        response = client.post(self.url, data={'username': user.username, 'password': user.password})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_credentials(self, client, user, faker):
        data = {
            'username': user.username,
            'password': faker.password
        }
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        ('is_active', 'status_code'),
        [(True, status.HTTP_200_OK), (False, status.HTTP_403_FORBIDDEN)],
        ids=['active', 'inactive']
    )
    def test_inactive_user_login_denied(self, client, user_factory, faker, is_active, status_code):
        password: str = faker.password()
        user: User = user_factory.create(password=password, is_active=is_active)
        data = {'username': user.username, 'password': password}
        response = client.post(self.url, data=data)

        assert response.status_code == status_code
