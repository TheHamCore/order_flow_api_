from .views import OrderViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='Order')

urlpatterns = router.urls