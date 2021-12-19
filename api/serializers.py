from rest_framework import serializers

from .models import Order, OrderDetail, Product


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['id', 'amount', 'price', 'product']
        depth = 1


class ProductSerializer(serializers.ModelSerializer):
    product = OrderDetailSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'product']


class OrderListSerializer(serializers.ModelSerializer):
    details = OrderDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'external_id', 'details']


class OrderRetrieveSerializer(serializers.ModelSerializer):
    details = OrderDetailSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'external_id', 'details']
