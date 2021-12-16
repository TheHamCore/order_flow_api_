import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.serializers import OrderListSerializer
from ..models import Order, OrderDetail, Product


class OrderApiTestCase(APITestCase):

    def setUp(self):
        order = Order.objects.create(external_id='test_order')
        order.save()
        product = Product.objects.create(name='test_product')
        product.save()
        self.details_test = OrderDetail.objects.create(
            order=order,
            amount=13,
            price=13.02,
            product=product
        )

        self.data = {
            "status": "accepted",
            "external_id": "PR-123-321-123",
            "details": [
                {
                    "amount": 10,
                    "price": "12.00",
                    "product": {
                        "name": "DropBox"
                    }
                }
            ]
        }

    def test_get_list(self):
        """Test for getting list of notes"""
        url = reverse('Order-list')
        response = self.client.get(url)

        serializer_data = OrderListSerializer([self.details_test.order], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_fail_detail(self):
        """Test for checking of error of getting a note"""
        url = reverse('Order-detail', kwargs={'pk': 25})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail(self):
        """Test for display a determined not"""
        url = reverse('Order-detail', kwargs={'pk': self.details_test.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('external_id'), 'test_order')

    def test_create(self):
        """Test for creating a new note"""
        url = reverse('Order-list')
        json_data = json.dumps(self.data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_update(self):
        """Test for updating note"""
        url = reverse('Order-detail', args=[self.details_test.id])
        response = self.client.put(url, data=self.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_delete_order(self):
        """Test for deleting note"""
        url = reverse('Order-detail', args=[self.details_test.id])
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
