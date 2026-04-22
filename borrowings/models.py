import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="book_borrowings"
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="user_book_borrowings"
    )

    def clean(self):
        borrow_date = self.borrow_date or datetime.date.today()

        if self.expected_return_date < borrow_date:
            raise ValidationError(
                "Expected return date can't be before borrow date!"
            )

        if (self.actual_return_date
                and self.actual_return_date < borrow_date):
            raise ValidationError(
                "Actual return date can't be before borrow date!"
            )

        if self.pk:
            borrowing = Borrowing.objects.get(pk=self.pk)
            if borrowing.actual_return_date:
                raise ValidationError(
                    "Borrowing has been already returned!"
                )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super().save(
            *args, force_insert, force_update, using, update_fields
        )

    class Meta:
        verbose_name_plural = "borrowings"

    def __str__(self) -> str:
        return (
            f"{self.user.email}, "
            f"{self.book.title}: "
            f"{self.borrow_date} - "
            f"{self.expected_return_date} - "
            f"{self.actual_return_date}"
        )
