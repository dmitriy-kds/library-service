import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from books.models import Book
from borrowings.models import Borrowing


class BorrowingModelTests(TestCase):
    def setUp(self):
        self.borrow_date = datetime.date.today()
        self.expected_return_date = (self.borrow_date +
                                     datetime.timedelta(days=7))
        self.book = Book.objects.create(
            title="Test",
            author="Test",
            cover="SOFT",
            inventory=10,
            daily_fee=10.55
        )
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="asdfg876T@"
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=self.borrow_date,
            expected_return_date=self.expected_return_date,
            actual_return_date=None,
            book=self.book,
            user=self.user
        )

    def test_create_borrowing(self):
        self.assertEqual(self.borrowing.borrow_date, self.borrow_date)
        self.assertEqual(
            self.borrowing.expected_return_date,
            self.expected_return_date
        )
        self.assertEqual(
            self.borrowing.actual_return_date,
            None
        )
        self.assertEqual(self.borrowing.book, self.book)
        self.assertEqual(self.borrowing.user, self.user)

    def test_borrowing_str(self):
        self.assertEqual(
            str(self.borrowing),
            f"{self.user.email}, "
            f"{self.book.title}: "
            f"{self.borrow_date} - "
            f"{self.expected_return_date} - "
            f"Not returned yet"
        )

    def test_expected_return_date_constraint(self):
        with self.assertRaisesRegex(
                ValidationError,
                "Expected return date can't be before borrow date!"
        ):
            Borrowing.objects.create(
                borrow_date=self.borrow_date,
                expected_return_date=(
                    self.borrow_date + datetime.timedelta(days=-1)
                ),
                actual_return_date=None,
                book=self.book,
                user=self.user
            )

    def test_actual_return_date_constraint(self):
        with self.assertRaisesRegex(
            ValidationError,
            "Actual return date can't be before borrow date!"
        ):
            Borrowing.objects.create(
                borrow_date=self.borrow_date,
                expected_return_date=self.expected_return_date,
                actual_return_date=(
                    self.borrow_date + datetime.timedelta(days=-1)
                ),
                book=self.book,
                user=self.user
            )

    def test_returning_same_borrowing_constraint(self):
        self.borrowing.actual_return_date = self.expected_return_date
        self.borrowing.save()
        self.borrowing.refresh_from_db()
        with self.assertRaisesRegex(
            ValidationError,
            "Borrowing has been already returned!"
        ):
            self.borrowing.actual_return_date = (
                    self.borrow_date + datetime.timedelta(days=10)
            )
            self.borrowing.save()
