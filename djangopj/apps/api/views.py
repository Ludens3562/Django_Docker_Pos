# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from apps.DBmaint.models import Product, Stock, Transaction, ReturnTransaction
from .serializers import TransactionSerializer, ProductSerializer, StockSerializer, ReturnTransactionSerializer
from django.utils import timezone
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination


# 商品情報に対する読み取り専用のViewSet
class ItemReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    JANコードに基づいて商品情報を取得するためのViewSet
    """
    permission_classes = [HasAPIKey | IsAuthenticated]  # APIキーを使用して認証
    serializer_class = ProductSerializer  # 使用するシリアライザーの指定

    def get_queryset(self):
        queryset = Product.objects.all()  # 全ての商品情報を取得
        jan = self.request.query_params.get("jan")  # リクエストからJANコードを取得
        if jan:
            queryset = queryset.filter(JAN=jan)  # JANコードが指定されていれば、そのコードに一致する商品のみをフィルタリング
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            # 指定されたJANコードの商品が見つからない場合は404エラーを返す
            return Response({"Error": "指定したJANコードに合致する製品が見つかりません。"}, status=status.HTTP_404_NOT_FOUND)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# 在庫情報に対する読み取り専用のViewSet
class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """
    JANコードもしくは店舗コードに基づいて在庫情報を取得するためのViewSet
    """
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = StockSerializer

    def get_queryset(self):
        # select_related を使用して関連する storecode と JAN データをあらかじめ取得
        queryset = Stock.objects.select_related('storecode', 'JAN').all()
        
        jan_code = self.request.query_params.get("jan")
        store_code = self.request.query_params.get("storecode")

        if jan_code:
            # JANコードに基づいてフィルタリング
            queryset = queryset.filter(JAN__JAN=jan_code)
        if store_code:
            # storecode に基づいてフィルタリング
            queryset = queryset.filter(storecode__storecode=store_code)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            # 指定されたJANコードおよびstorecodeの在庫が見つからない場合は404エラーを返す
            return Response({"Error": "指定した店舗コードまたはJANに合致する在庫が見つかりません。"}, status=status.HTTP_404_NOT_FOUND)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# 取引情報に対するCRUD操作を行うビュー
class TransactionViewSet(viewsets.ModelViewSet):
    """
    取引情報に対するCRUD操作を行うためのViewSet
    """
    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagenation_class = LimitOffsetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # データのバリデーション
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)  # 部分更新かどうか
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # データのバリデーション
        self.perform_update(serializer)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        sale_id = request.query_params.get('sale_id', None)
        queryset = self.get_queryset()
        if sale_id is not None:
            queryset = queryset.filter(sale_id=sale_id)
        if not queryset.exists():
            return Response({"Error": "指定した売上IDに合致する取引が見つかりません。"}, status=status.HTTP_404_NOT_FOUND)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"Error": "指定した取引IDに合致する取引が見つかりません。"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TestViewSet(ViewSet):
    def list(self, request):
        data = {
            'message': 'Connection successful!',
            'remote address': request.META.get("REMOTE_ADDR"),
            'current_time': timezone.now(),
        }
        return Response(data)


class ReturnTransactionViewSet(viewsets.ModelViewSet):
    """
    返品取引情報に対するCRUD操作を行うためのViewSet
    """
    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = ReturnTransaction.objects.all()
    serializer_class = ReturnTransactionSerializer
    pagination_class = LimitOffsetPagination  # pagenation_class から pagination_class に修正

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # データのバリデーション
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)  # 部分更新かどうか
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # データのバリデーション
        self.perform_update(serializer)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        return_id = request.query_params.get('return_id', None)
        queryset = self.get_queryset()
        if return_id is not None:
            queryset = queryset.filter(return_id=return_id)
            if not queryset.exists():
                return Response({"Error": "指定した返品IDに合致する取引が見つかりません。"}, status=status.HTTP_404_NOT_FOUND)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"Error": "指定した返品IDに合致する取引が見つかりません。"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)