import pytest
from django.urls import reverse
from rest_framework import status

from core.models import User
from tests.utils import BaseTestCase


@pytest.mark.django_db
class TestUpdatePassword(BaseTestCase):
    url = reverse('core:update_password')

    def test_auth_required(self, client):
        response = client.patch(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_old_password(self, auth_client, faker):
        expected_response = {'old_password': ['field is incorrect']}
        data = {'old_password': faker.password(), 'new_password': faker.password()}
        response = auth_client.patch(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == expected_response

    def test_weak_new_password(self, client, faker, user_factory, invalid_password):
        password: str = faker.password()
        user: User = user_factory.create(password=password)
        client.force_login(user)
        data = {'old_password': password, 'new_password': invalid_password}
        response = client.patch(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_success(self, client, user_factory, faker):
        old_password: str = faker.password()
        user: User = user_factory.create(password=old_password)
        new_password: str = faker.password()
        client.force_login(user)
        data = {'old_password': old_password, 'new_password': new_password}
        response = client.patch(self.url, data=data)

        assert response.status_code == status.HTTP_200_OK
        assert not response.data
        user.refresh_from_db(fields=('password',))
        assert user.check_password(new_password)
