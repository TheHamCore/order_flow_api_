from django.test import TestCase

from api.serializers import OrderDetailSerializer, ProductSerializer
from ..models import OrderDetail, Product


class DetailSerializerTestCase(TestCase):
    def test_detail_serializer(self):
        product_1 = Product.objects.create(name='prod')
        detail = OrderDetail.objects.create(amount=13, price=13.00, product=product_1)
        data = OrderDetailSerializer(detail).data
        expected_data = {
            'id': detail.id,
            'amount': 13,
            'price': '13.00',
            'product': {
                'id': product_1.id,
                'name': 'prod',
            }
        }
        self.assertEqual(expected_data, data)


class ProductSerializerTestCase(TestCase):
    def test_product_serializer(self):
        product = Product.objects.create(name='prod')
        data = ProductSerializer(product).data
        expected_data = {
            'id': product.id,
            'name': 'prod',
            'product': []
        }
        self.assertEqual(expected_data, data)
