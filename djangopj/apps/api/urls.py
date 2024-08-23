from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemReadOnlyViewSet, StockViewSet, TransactionViewSet, TestViewSet, ReturnTransactionViewSet

router = DefaultRouter()
router.register(r'test', TestViewSet, basename='test')
router.register(r'items', ItemReadOnlyViewSet, basename='item')
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'returntransactions', ReturnTransactionViewSet, basename='returntransaction')

urlpatterns = [
    path('', include(router.urls)),
]
