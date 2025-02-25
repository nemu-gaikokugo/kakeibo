from django.http import HttpRequest
from django.test import TestCase

class TopPageViewTest(TestCase):
    def test_top_returns_200(self):
        response=self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_top_returns_expected_content(self):
        response=self.client.get("/")
        self.assertEqual(response.content, b"Hello World")