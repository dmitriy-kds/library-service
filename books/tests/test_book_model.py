from django.db import IntegrityError
from django.test import TestCase

from books.models import Book


class BookModelTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title = "Test",
            author = "Test",
            cover = "SOFT",
            inventory=10,
            daily_fee=10.55
        )

    def test_create_book(self):
        self.assertEqual(self.book.author, "Test")
        self.assertEqual(self.book.title, "Test")
        self.assertEqual(self.book.cover, "SOFT")
        self.assertEqual(self.book.inventory, 10)
        self.assertEqual(self.book.daily_fee, 10.55)


    def test_book_str(self):
        self.assertEqual(
            str(self.book),
            f"{self.book.title} by {self.book.author}"
        )

    def test_unique_book_constraint(self):
        with self.assertRaises(IntegrityError):
            Book.objects.create(
            title = "Test",
            author = "Test",
            cover = "HARD",
            inventory=5,
            daily_fee=11.55
        )
