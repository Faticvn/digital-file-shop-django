from django.test import TestCase
from django.contrib.auth import get_user_model
from files.models import DigitalFile


class OrderFlowTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.seller = User.objects.create_user(
            username="seller_test",
            password="12345678",
            role="seller"
        )

        self.buyer = User.objects.create_user(
            username="buyer_test",
            password="12345678",
            role="buyer"
        )

        self.file = DigitalFile.objects.create(
            seller=self.seller,
            type="article",
            title="فایل تست",
            price=10000,
            file="test.txt",
            is_active=True
        )

    def test_add_to_cart(self):
        self.client.login(username="buyer_test", password="12345678")
        response = self.client.post(f"/orders/cart/add/{self.file.id}/")
        self.assertEqual(response.status_code, 302)

    def test_file_visible(self):
        response = self.client.get("/")
        self.assertContains(response, "فایل تست")