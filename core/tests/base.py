import datetime

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing


class BookBaseTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=50,
            daily_fee="9.99"
        )


class UserBaseTestCase(BookBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super(UserBaseTestCase, cls).setUpTestData()
        cls.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="asdf6789%Q"
        )
        cls.admin = get_user_model().objects.create_superuser(
            email="admin@admin.com",
            password="asdf6789%Q"
        )


class BorrowingBaseTestCase(UserBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super(BorrowingBaseTestCase, cls).setUpTestData()
        cls.user_borrowing_1 = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() +
                                 datetime.timedelta(days=10),
            book=cls.book,
            user=cls.user
        )
        cls.user_borrowing_2 = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() +
                                 datetime.timedelta(days=5),
            book=cls.book,
            user=cls.user
        )
        cls.admin_borrowing_1 = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() +
                                 datetime.timedelta(days=10),
            book=cls.book,
            user=cls.admin
        )
        cls.admin_borrowing_2 = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() +
                                 datetime.timedelta(days=5),
            book=cls.book,
            user=cls.admin
        )
