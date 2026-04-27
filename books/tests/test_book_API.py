from django.urls import reverse
from rest_framework import status

from core.tests.base import BookBaseTestCase, UserBaseTestCase


class PublicBookApiTests(BookBaseTestCase):

    def test_unauthorized_book_list_success(self):
        url = reverse("books:book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.book.title)

    def test_unauthorized_book_detail_success(self):
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.book.id)

    def test_unauthorized_user_cannot_create_book(self):
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": "9.99"
        }
        url = reverse("books:book-list")
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedBookApiTests(UserBaseTestCase):
    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_authorized_book_list_success(self):
        url = reverse("books:book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.book.title)

    def test_authorized_book_detail_success(self):
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.book.id)

    def test_authorized_user_cannot_create_book(self):
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": "9.99"
        }
        url = reverse("books:book-list")
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(UserBaseTestCase):
    def setUp(self):
        self.client.force_authenticate(self.admin)

    def test_admin_create_book_success(self):
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": "9.99"
        }
        url = reverse("books:book-list")
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_update_book_success(self):
        payload = {
            "title": "Updated Book",
            "author": "Updated Author",
            "cover": "SOFT",
            "inventory": 7,
            "daily_fee": "7.77"
        }
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.put(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], payload["title"])
        self.assertEqual(response.data["author"], payload["author"])
        self.assertEqual(response.data["cover"], payload["cover"])
        self.assertEqual(response.data["inventory"], payload["inventory"])
        self.assertEqual(response.data["daily_fee"], payload["daily_fee"])

    def test_admin_partial_update_book_success(self):
        payload = {
            "author": "Updated Author",
        }
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.patch(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, payload["author"])

    def test_admin_cannot_create_book_with_same_title_and_author(self):
        payload = {
            "title": self.book.title,
            "author": self.book.author,
            "cover": "SOFT",
            "inventory": 11,
            "daily_fee": "99.99"
        }
        url = reverse("books:book-list")
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_delete_book_success(self):
        url = reverse("books:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
