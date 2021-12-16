from django.db import models


class Order(models.Model):
    """class for creating Order model"""
    NEW = 'new'
    ACCEPTED = 'accepted'
    FAILED = 'failed'

    order_status = [
        (NEW, 'new'),
        (ACCEPTED, 'accepted'),
        (FAILED, 'failed'),
    ]

    status = models.CharField(max_length=12, choices=order_status, default='new', blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    external_id = models.CharField(max_length=128)

    def __str__(self):
        return f'Order № {self.external_id}'


class Product(models.Model):
    """class for creating Product model"""
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class OrderDetail(models.Model):
    """class for creating OrderDetail model"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='details',
                              null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='product',
                                null=True)
    price = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)

    def __str__(self):
        return f'Detail for {self.order}, detail for product {self.product}'
