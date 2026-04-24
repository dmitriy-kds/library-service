import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer
from core.tests.base import BorrowingBaseTestCase


class PublicBorrowingApiTests(APITestCase):

    def test_unauthorized_user_cannot_access_borrowings_list(self):
        url = reverse("borrowings:borrowings-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_create_borrowings(self):
        url = reverse("borrowings:borrowings-list")
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedBorrowingApiTests(BorrowingBaseTestCase):
    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_only_authorized_users_borrowings_in_list(self):
        url = reverse("borrowings:borrowings-list")
        response = self.client.get(url)

        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingListSerializer(
            borrowings,
            many=True,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_authorized_user_borrowings_detail_success(self):
        url = reverse(
            "borrowings:borrowings-detail",
            kwargs={"pk": self.user_borrowing_1.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authorized_user_cannot_access_other_users_borrowing_detail(
            self
    ):
        url = reverse(
            "borrowings:borrowings-detail",
            kwargs={"pk": self.admin_borrowing_1.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authorized_user_borrowing_create_success(self):
        inventory = self.book.inventory
        payload ={
            "expected_return_date": datetime.date.today() +
                                    datetime.timedelta(days=1),
            "book": self.book.id,
        }
        url = reverse(
            "borrowings:borrowings-list"
        )
        response = self.client.post(url, data=payload)
        self.book.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.book.inventory, (inventory - 1))

    def test_cannot_create_borrowing_if_inventory_is_zero(self):
        self.book.inventory = 0
        self.book.save()
        payload ={
            "expected_return_date": datetime.date.today() +
                                    datetime.timedelta(days=1),
            "book": self.book.id,
        }
        url = reverse(
            "borrowings:borrowings-list"
        )
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_borrowing_for_another_user(self):
        payload ={
            "expected_return_date": datetime.date.today() +
                                    datetime.timedelta(days=1),
            "book": self.book.id,
            "user": self.admin.id,
        }
        url = reverse(
            "borrowings:borrowings-list"
        )
        response = self.client.post(url, data=payload)
        self.assertNotEqual(self.admin.pk, response.data["user"])
        self.assertEqual(self.user.pk, response.data["user"])

    def test_authenticated_user_return_borrowing(self):
        self.book.inventory = 0
        self.book.save()
        inventory = self.book.inventory
        actual_return_date = (datetime.date.today() +
                              datetime.timedelta(days=5))
        payload ={
            "actual_return_date": actual_return_date
        }
        url = reverse(
            "borrowings:borrowings-return-borrowing",
            kwargs={"pk": self.user_borrowing_1.id}
        )
        response = self.client.post(url, data=payload)
        self.user_borrowing_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            inventory + 1,
            self.user_borrowing_1.book.inventory
        )
        self.assertEqual(
            self.user_borrowing_1.actual_return_date,
            actual_return_date
        )

    def test_is_active_filter_for_authenticated_user(self):
        self.user_borrowing_2.actual_return_date = datetime.date.today()
        self.user_borrowing_2.save()
        url = reverse("borrowings:borrowings-list")
        response = self.client.get(url, data={"is_active": "true"})

        borrowings = Borrowing.objects.filter(
            actual_return_date=None,
            user=self.user
        )
        serializer = BorrowingListSerializer(
            borrowings,
            many=True,
        )
        self.assertEqual(response.data, serializer.data)

        response = self.client.get(url, data={"is_active": "false"})

        borrowings = Borrowing.objects.filter(
            actual_return_date__isnull=False,
            user=self.user
        )
        serializer = BorrowingListSerializer(
            borrowings,
            many=True,
        )
        self.assertEqual(response.data, serializer.data)

    def test_authenticated_user_cannot_apply_user_id_filter(self):
        url = reverse("borrowings:borrowings-list")
        response = self.client.get(url, data={"user_id": self.admin.id})

        user_borrowings = Borrowing.objects.filter(user=self.user.id)
        user_serializer = BorrowingListSerializer(
            user_borrowings,
            many=True,
        )
        self.assertEqual(response.data, user_serializer.data)


class AdminBorrowingApiTests(BorrowingBaseTestCase):
    def setUp(self):
        self.client.force_authenticate(self.admin)

    def test_admin_sees_all_users_borrowings_in_list(self):
        url = reverse("borrowings:borrowings-list")
        response = self.client.get(url)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(
            borrowings,
            many=True,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_is_active_and_user_id_filter_for_admin_user(self):
        self.user_borrowing_2.actual_return_date = datetime.date.today()
        self.user_borrowing_2.save()
        url = reverse("borrowings:borrowings-list")
        response = self.client.get(
            url,
            data={
                "is_active": "true",
            }
        )

        borrowings = Borrowing.objects.filter(actual_return_date=None)
        serializer = BorrowingListSerializer(
            borrowings,
            many=True,
        )
        self.assertEqual(response.data, serializer.data)

        response = self.client.get(
            url,
            data={
                "user_id": self.user.id
            }
        )

        borrowings = Borrowing.objects.filter(user=self.user.id)
        serializer = BorrowingListSerializer(
            borrowings,
            many=True,
        )
        self.assertEqual(response.data, serializer.data)
