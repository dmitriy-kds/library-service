import asyncio
from typing import Any

from django.db import transaction
from django.db.models import QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from borrowings.models import Borrowing
from borrowings.notifications import notify_borrowing_created
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer
)


class BorrowingsViewSet(viewsets.ModelViewSet):

    @extend_schema(
        request=BorrowingReturnSerializer,
        responses=BorrowingReturnSerializer
    )
    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk: int = None) -> Response:
        """Endpoint for returning borrowed books"""
        borrowing = Borrowing.objects.get(pk=pk)
        serializer = BorrowingReturnSerializer(borrowing, data=request.data)
        with transaction.atomic():
            serializer.is_valid(raise_exception=True)
            serializer.save()
            book = borrowing.book
            book.inventory += 1
            book.save()
        return Response(serializer.data)

    def get_serializer_class(self) -> type[ModelSerializer]:
        serializer_class = BorrowingListSerializer

        if self.action == "retrieve":
            serializer_class = BorrowingDetailSerializer
        elif self.action in ("create", "update", "partial_update"):
            serializer_class = BorrowingCreateSerializer
        elif self.action == "return_borrowing":
            serializer_class = BorrowingReturnSerializer
        return serializer_class

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        queryset = Borrowing.objects.all().select_related("user", "book")
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        user_id = self.request.query_params.get("user_id", None)
        is_active = self.request.query_params.get("is_active", None)

        if user.is_staff and user_id:
            queryset = queryset.filter(user_id=user_id)
        if is_active == "true":
            queryset = queryset.filter(actual_return_date=None)
        elif is_active == "false":
            queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def perform_create(self, serializer: BorrowingCreateSerializer) -> None:
        with transaction.atomic():
            user = self.request.user
            book = serializer.validated_data["book"]
            book.inventory -= 1
            book.save()
            serializer.save(user=user)
        notify_borrowing_created(user, serializer.validated_data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.INT,
                description="Filter by user id "
                            "(ex. ?user_id=1)",
            ),
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.BOOL,
                description="Filter by borrowing status "
                            "(ex. ?is_active=true or ?is_active=true)",
            )
        ]
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
