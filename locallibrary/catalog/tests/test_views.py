from django.test import TestCase
from django.urls import reverse
from catalog.models import Book
from django.contrib.auth.models import User


class BookListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Tạo 13 sách để test phân trang
        number_of_books = 13
        for book_num in range(number_of_books):
            Book.objects.create(
                title=f"Book {book_num}", summary="Summary", isbn=f"000000000{book_num}"
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/catalog/books/")
        self.assertEqual(response.status_code, 200)

    def test_view_accessible_by_name(self):
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/book_list.html")

    def test_pagination_is_ten(self):
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["book_list"]), 10)

    def test_lists_all_books(self):
        response = self.client.get(reverse("books") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(len(response.context["book_list"]), 3)
        