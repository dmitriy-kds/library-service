import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from users.serializers import UserSerializer


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.SerializerMethodField()
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        )

    def get_book(self, obj: Borrowing) -> str:
        return f"'{obj.book.title}' by {obj.book.author}"


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "user"
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "user"
        )

    def validate(self, attrs: dict) -> dict:
        borrow_date = datetime.date.today()
        if attrs["expected_return_date"] < borrow_date:
            raise ValidationError(
                "Expected return date can't be before borrow date!"
            )

        if attrs["book"].inventory < 1:
            raise ValidationError(
                "No copies of this book available!"
            )

        return attrs


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "actual_return_date",
            "book",
        )
        read_only_fields = ("id", "book")

    def validate(self, attrs: dict) -> dict:
        if attrs["actual_return_date"] < self.instance.borrow_date:
            raise ValidationError(
                "Actual return date can't be before borrow date!"
            )

        if self.instance.actual_return_date:
            raise ValidationError(
                "Borrowing has been already returned!"
            )
        return attrs
