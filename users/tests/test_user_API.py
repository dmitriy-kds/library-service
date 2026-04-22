from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import User

CREATE_USER_URL = reverse("users:create")
TOKEN_URL = reverse("users:token_obtain_pair")
TOKEN_REFRESH_URL = reverse("users:token_refresh")
ME_URL = reverse("users:manage")


def create_user(**params: Any) -> User:
    defaults = {
        "email": "test@test.com",
        "password": "*T12345eSt",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


class PublicUserApiTests(APITestCase):
    def test_create_user_success(self):
        response = self.client.post(
            CREATE_USER_URL, {"email": "a@a.com", "password": "132kltjnF"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_password_too_short(self):
        response = self.client.post(
            CREATE_USER_URL, {"email": "a@a.com", "password": "2k&F"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_duplicate_email(self):
        create_user(email="a@a.com", password="1l3kng1pi9F")
        response = self.client.post(
            CREATE_USER_URL, {"email": "a@a.com", "password": "1l3kng1pi9F"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtain_token_valid_credentials(self):
        payload = {"email": "b@b.com", "password": "qwrkjn293"}
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_obtain_token_wrong_password(self):
        payload = {"email": "b@b.com", "password": "qwrkjn293"}
        create_user(**payload)
        response = self.client.post(
            TOKEN_URL,
            {
                "email": "b@b.com",
                "password": "qwrkjn2931",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_nonexistent_user(self):
        response = self.client.post(
            TOKEN_URL, {"email": "f@d.com", "password": "qwrkjn29"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_success(self):
        payload = {"email": "b@b.com", "password": "qwrkjn293"}
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        refresh_token = response.data["refresh"]
        response = self.client.post(TOKEN_REFRESH_URL, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_token_invalid(self):
        response = self.client.post(TOKEN_REFRESH_URL, {"refresh": "12345"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_unauthenticated(self):
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self):
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_profile_no_password(self):
        response = self.client.get(ME_URL)
        self.assertNotIn("password", response.data)

    def test_create_user_password_not_in_response(self):
        response = self.client.post(
            CREATE_USER_URL, {"email": "a@a.com", "password": "testpass123"}
        )
        self.assertNotIn("password", response.data)

    def test_update_user_email(self):
        response = self.client.patch(ME_URL, {"email": "updated@email.com"})
        self.assertEqual("updated@email.com", response.data["email"])

    def test_update_user_password(self):
        response = self.client.patch(ME_URL, {"password": "newPassword1*"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(check_password("newPassword1*", self.user.password))

    def test_update_user_password_too_short(self):
        response = self.client.patch(ME_URL, {"password": "1*rH"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_full_update_user(self):
        response = self.client.put(
            ME_URL, {"email": "new_email@email.com", "password": "1*rH24t"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("new_email@email.com", response.data["email"])
        self.assertTrue(check_password("1*rH24t", self.user.password))
