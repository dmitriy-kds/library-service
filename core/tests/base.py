from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from books.models import Book


class BookBaseTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee="9.99"
        )


class UserBaseTestCase(BookBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee="9.99"
        )
        cls.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="asdf6789%Q"
        )
        cls.admin = get_user_model().objects.create_superuser(
            email="admin@admin.com",
            password="asdf6789%Q"
        )


