import pytest
from django.urls import reverse

from tests.utils import BaseTestCase
from todolist import settings


@pytest.mark.django_db
class TestProfileRetrieve(BaseTestCase):
    url = reverse('core:profile')

    def test_auth_required(self, client):
        response = client.get(self.url)
        assert response.status_code == 403

    def test_success(self, auth_client, user):
        expected_response = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        response = auth_client.get(self.url)
        assert response.status_code == 200
        assert response.data == expected_response


@pytest.mark.django_db
class TestProfileUpdate(BaseTestCase):
    url = reverse('core:profile')

    def test_auth_required(self, client, faker):
        response = client.get(self.url, data=faker.pydict(1))
        assert response.status_code == 403

    @pytest.mark.parametrize('user__email', ['test@email.ru'])
    def test_update_profile(self, client, user):
        expected_response = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': 'update_test@mail.ru'
        }
        client.force_login(user)
        response = client.patch(self.url, data={'email': 'update_test@mail.ru'})
        assert response.status_code == 200
        assert response.data == expected_response


@pytest.mark.django_db
class TestDestroyProfile(BaseTestCase):
    url = reverse('core:profile')

    def test_auth_required(self, client):
        response = client.get(self.url)
        assert response.status_code == 403

    def test_user_not_deleted(self, auth_client, django_user_model):
        initial_count = django_user_model.objects.count()
        response = auth_client.delete(self.url)
        assert response.status_code == 204
        assert django_user_model.objects.count() == initial_count

    @pytest.mark.parametrize('backend', settings.AUTHENTICATION_BACKENDS)
    def test_cleanup_cookie(self, client, user, backend):
        client.force_login(user, backend=backend)
        assert client.cookies['sessionid'].value
        response = client.delete(self.url)
        assert response.status_code == 204
        assert not client.cookies['sessionid'].value
