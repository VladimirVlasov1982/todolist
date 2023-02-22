import pytest
from django.urls import reverse
from tests.utils import BaseTestCase
from rest_framework import status


@pytest.mark.django_db
class TestSignup(BaseTestCase):
    url = reverse('core:signup')

    def test_passwords_missmatch(self, client, faker):
        expected_response = {'password_repeat': ['Passwords must match']}
        data = {
            'username': faker.user_name(),
            'password': faker.password(),
            'password_repeat': faker.password()
        }
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == expected_response

    def test_invalid_password(self, client, faker, invalid_password):
        data = {
            'username': faker.user_name(),
            'password': invalid_password,
            'password_repeat': invalid_password
        }
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_success(self, client, user_factory, django_user_model):
        assert not django_user_model.objects.count()

        user_data = user_factory.build()
        response = client.post(self.url, data={
            'username': user_data.username,
            'password': user_data.password,
            'password_repeat': user_data.password
        })
        assert response.status_code == status.HTTP_201_CREATED

        assert django_user_model.objects.count() == 1
        new_user = django_user_model.objects.last()
        assert response.data == {
            'id': new_user.id,
            'username': user_data.username,
            'first_name': '',
            'last_name': '',
            'email': ''
        }
        assert new_user.password != user_data.password
        assert new_user.check_password(user_data.password)
