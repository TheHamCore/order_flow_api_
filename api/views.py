from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from .pagination import ContentRangeHeaderPagination
from .serializers import OrderDetailSerializer, ProductSerializer, \
    OrderListSerializer, OrderRetrieveSerializer
from api.models import Order, OrderDetail, Product
from rest_framework.viewsets import ModelViewSet


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    pagination_class = ContentRangeHeaderPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['external_id', 'status']
    ordering_fields = ['id', 'status', 'created_at']

    def retrieve(self, request, *args, **kwargs):
        """
        url: /api/v1/orders/{id}

        response:
            {
                "id": 1,
                "status": "new",
                "created_at": "2021-01-01T00:00:00",
                "external_id": "PR-123-321-123-new", # change this string
                "details": [{
                    "id": 1,
                    "product": {"id": 4, "name": "Dropbox"},
                    "amount": 10,
                    "price": "12.00"
                }]
            }
        """
        instance = self.get_object()
        serializer = OrderRetrieveSerializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        payload:
        {
            "external_id": "PR-123-321-123",
            "details": [{
                "product": {"id": 4, "name":"Dropbox"},
                "amount": 10,
                "price": "12.00"
            }]
        }

        response:
        {
            "id": 5,
            "status": "new",
            "created_at": "2021-12-18T21:15:43.523149Z",
            "external_id": "PR-123-321-123",
            "details": [
                {
                    "id": 4,
                    "amount": 10,
                    "price": "12.00",
                    "product": {
                        "id": 4,
                        "name": ""Dropbox""
                    }
                }
            ]
        }
        """
        order = Order.objects.create(external_id=request.data['external_id'])
        for data in request.data['details']:
            product = Product.objects.create(name=data['product']['name'])
            OrderDetail.objects.create(amount=data['amount'],
                                       price=data['price'],
                                       product=product,
                                       order=order)

        serializer = OrderListSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'PUT' or 'PATCH':
            serializer_class = OrderListSerializer

        return serializer_class

    def update(self, request, *args, **kwargs):
        """
        case 1: status = 'new'
        payload:
         {
            "id": 1,
            "status": "new",
            "created_at": "2021-01-01T00:00:00",
            "external_id": "PR-123-321-123-new", # change this string
            "details": [{
                "id": 1,
                "product": {"id": 4, "name": "Dropbox"},
                "amount": 10,
                "price": "12.00"
            }]
        }

        response:
        {
            "id": 1,
            "status": "new",
            "created_at": "2021-01-01T00:00:00",
            "external_id": "PR-124-444-444-new", # change this string
            "details": [{
                "id": 1,
                "product": {"id": 4, "name": "Dropbox"},
                "amount": 10,
                "price": "12.00"
            }]
        }

        case 2: status = 'accepted' OR 'failed'
        payload:
         {
            "id": 1,
            "status": "accepted",
            "created_at": "2021-01-01T00:00:00",
            "external_id": "PR-123-321-123-new",
            "details": [{
                "id": 1,
                "product": {"id": 4, "name": "Dropbox"},
                "amount": 10,
                "price": "12.00"
            }]
        }

        response:
        {
            "error": "you cannot change data with status 'failed' or 'accepted'"
        }
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if instance.status == 'new':
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "you cannot change data with status 'failed' or 'accepted'"},
                            status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        """
        case 1: status = 'new' OR 'failed'
        url:
            /api/v1/orders/{int}
        response:
            {
                "success": "The data has deleted"
            }


        case 2: status = 'accepted'
        url:
            /api/v1/orders/{int}
        response:
            {
                "error": "you cannot delete data with status 'accepted'"
            }

        """
        instance = self.get_object()
        if instance.status == 'accepted':
            return Response({"error": "you cannot delete data with status 'accepted'"},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            self.perform_destroy(instance)
            return Response({"success": "The data has deleted"},
                            status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True)
    def accept(self, request, pk=None):
        """
        This method allows changing status. Status "failed" changes to "accepted".

        url request:
            api/v1/orders/{id}/accept
        payload:
            {
                "id": 1,
                "status": "failed",
                "created_at": "2021-01-01T00:00:00",
                "external_id": "PR-123-321-123-new",
                "details": [{
                    "id": 1,
                    "product": {"id": 4, "name": "Dropbox"},
                    "amount": 10,
                    "price": "12.00"
                }]
            }
        response:
            {
                "id": 1,
                "status": "accepted",
                "created_at": "2021-01-01T00:00:00",
                "external_id": "PR-123-321-123-new",
                "details": [{
                    "id": 1,
                    "product": {"id": 4, "name": "Dropbox"},
                    "amount": 10,
                    "price": "12.00"
                }]
            }
        """
        obj = self.get_object()
        obj.external_id = obj.external_id
        obj.status = obj.status

        if obj.status == 'failed':
            obj.status = 'accepted'
            obj.save()
            serializer = OrderListSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif obj.status == 'accepted':
            serializer = OrderListSerializer(obj)
            return Response(serializer.data)

    @action(methods=['post'], detail=True)

    def fail(self, request, pk=None):
        """
        This method allows changing status. Status "accepted" changes to "failed".

        url request:
            api/v1/orders/{id}/fail
        payload:
            {
                "id": 1,
                "status": "accepted",
                "created_at": "2021-01-01T00:00:00",
                "external_id": "PR-123-321-123-new",
                "details": [{
                    "id": 1,
                    "product": {"id": 4, "name": "Dropbox"},
                    "amount": 10,
                    "price": "12.00"
                }]
            }
        response:
            {
                "id": 1,
                "status": "failed",
                "created_at": "2021-01-01T00:00:00",
                "external_id": "PR-123-321-123-new",
                "details": [{
                    "id": 1,
                    "product": {"id": 4, "name": "Dropbox"},
                    "amount": 10,
                    "price": "12.00"
                }]
            }
        """
        obj = self.get_object()
        obj.external_id = obj.external_id
        obj.status = obj.status

        if obj.status == 'accepted':
            obj.status = 'failed'
            obj.save()
            serializer = OrderListSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif obj.status == 'failed':
            serializer = OrderListSerializer(obj)
            return Response(serializer.data)


class OrderDetailViewSet(ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
