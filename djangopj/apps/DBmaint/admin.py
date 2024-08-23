from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Sum, F, FloatField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from django import forms
from .models import (
    Store,
    Product,
    Stock,
    Transaction,
    SaleProduct,
    SaleSummary,
    ReturnTransaction,
    ReturnProduct,
    Coupon,
)


# Resources
class BaseResource(resources.ModelResource):
    exclude = ("id",)


class StoreResource(resources.ModelResource):
    class Meta:
        model = Store
        import_id_fields = ("storecode",)
        fields = ("name",)


class ProductResource(BaseResource):
    class Meta:
        model = Product
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ("JAN",)
        fields = ("JAN", "name", "price", "tax")


class StockResource(BaseResource):
    class Meta:
        model = Stock
        import_id_fields = ("storecode", "JAN")


class TransactionResource(BaseResource):
    class Meta:
        model = Transaction
        import_id_fields = ("id",)


class SaleProductResource(BaseResource):
    class Meta:
        model = SaleProduct
        import_id_fields = ("transaction", "JAN")


class ReturnTransactionResource(BaseResource):
    class Meta:
        model = ReturnTransaction
        import_id_fields = ("id",)


class ReturnProductResource(BaseResource):
    class Meta:
        model = ReturnProduct
        import_id_fields = ("id",)


# Inlines
class BaseInline(admin.TabularInline):
    extra = 0


class SaleProductInline(BaseInline):
    model = SaleProduct


class StockInline(BaseInline):
    model = Stock


class ReturnProductInline(BaseInline):
    model = ReturnProduct


# Filters
class NegativeQuantityFilter(admin.SimpleListFilter):
    title = "在庫がマイナスのもの"
    parameter_name = "negative_quantity"

    def lookups(self, request, model_admin):
        return (("negative", "マイナス在庫"),)

    def queryset(self, request, queryset):
        if self.value() == "negative":
            return queryset.filter(quantity__lt=0)
        return queryset


class StoreCodeNameFilter(admin.SimpleListFilter):
    title = "店舗"
    parameter_name = "storecode"

    def lookups(self, request, model_admin):
        stores = Store.objects.all()
        return [(store.storecode, f"{store.storecode} ({store.name})") for store in stores]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(storecode__storecode=self.value())
        return queryset


# Admin Models
class StoreAdmin(ImportExportModelAdmin):
    resource_class = StoreResource
    list_display = ("storecode", "name")
    search_fields = ("storecode", "name")


class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ("JAN", "name", "price", "tax")
    search_fields = ("JAN", "name")
    list_per_page = 50
    inlines = [StockInline]
    actions = ["regenerate_stock"]

    @transaction.atomic
    def regenerate_stock(self, request, queryset):
        try:
            stores = Store.objects.all()
            batch_size = 50  # バッチサイズを決定
            for i in range(0, queryset.count(), batch_size):
                batch = queryset[i:i + batch_size]
                for product in batch:
                    for store in stores:
                        Stock.objects.update_or_create(storecode=store, JAN=product, defaults={"quantity": 0})
            self.message_user(request, "選択した商品の在庫が再生成されました。", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"在庫の再生成に失敗しました: {str(e)}", messages.ERROR)
            transaction.set_rollback(True)

    regenerate_stock.short_description = "選択した商品の在庫を再生成"


class StockAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = StockResource
    list_display = ("storecode", "JAN", "quantity")
    list_filter = (StoreCodeNameFilter, NegativeQuantityFilter)
    search_fields = ("storecode__storecode", "JAN__JAN")
    list_per_page = 50
    actions = ["add_stock", "reset_stock"]

    @transaction.atomic
    def add_stock(self, request, queryset):
        try:
            for stock in queryset:
                stock.quantity += 10
                stock.save()
            self.message_user(request, "選択した商品の在庫を10個加算しました。", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"在庫の加算に失敗しました: {str(e)}", messages.ERROR)
            transaction.set_rollback(True)

    add_stock.short_description = "選択した商品の在庫を10個加算"

    @transaction.atomic
    def reset_stock(self, request, queryset):
        try:
            queryset.update(quantity=0)
            self.message_user(request, "選択した在庫をリセットしました。", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"在庫のリセットに失敗しました: {str(e)}", messages.ERROR)
            transaction.set_rollback(True)

    reset_stock.short_description = "選択した在庫をリセット"


class TransactionAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = TransactionResource
    list_display = (
        "sale_id",
        "sale_type",
        "sale_date",
        "storecode",
        "staffcode",
        "purchase_points",
        "total_amount",
        "deposit",
        "change",
    )
    search_fields = ("sale_id", "storecode__storecode", "staffcode__staffcode")
    list_filter = ("sale_type", "sale_date")
    ordering = ("-id",)
    inlines = [SaleProductInline]


class SaleProductAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = SaleProductResource
    list_display = ("transaction_id", "JAN", "name", "price", "tax", "points")
    search_fields = ("transaction__id", "JAN__JAN", "name")


class SaleSummaryAdmin(admin.ModelAdmin):
    date_hierarchy = "sale_date"
    list_filter = ("sale_date",)
    change_list_template = "admin/sale_summary_change_list.html"

    def get_queryset(self, request):
        return super().get_queryset(request)

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)

        product_names = Product.objects.filter(JAN=OuterRef("JAN__JAN")).values("JAN")[:1]

        summary = (
            SaleProduct.objects.filter(transaction__in=qs)
            .values("JAN__JAN", "transaction__sale_date__date")
            .annotate(
                name=Subquery(product_names.values("name")[:1]),
                total_amount=Coalesce(Sum(F("price") * F("points")), 0, output_field=FloatField()),
                total_points=Coalesce(Sum("points"), 0),
            )
            .order_by("-total_points", "-transaction__sale_date__date")
        )

        total_amount = summary.aggregate(total=Sum("total_amount"))["total"] or 0
        total_points = summary.aggregate(total=Sum("total_points"))["total"] or 0

        extra_context = extra_context or {}
        extra_context["summary"] = summary
        extra_context["total_amount"] = total_amount
        extra_context["total_points"] = total_points

        return super().changelist_view(request, extra_context=extra_context)


class ReturnTransactionAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = ReturnTransactionResource
    list_display = (
        "return_type",
        "return_id",
        "originSaleid",
        "storecode",
        "staffcode",
        "reason",
        "return_points",
        "tax_10_percent",
        "tax_8_percent",
        "tax_amount",
        "return_amount",
        "return_date",
    )
    search_fields = ("return_id", "originSaleid")
    list_filter = ("return_type", "return_date")
    ordering = ("-id",)
    inlines = [ReturnProductInline]


class ReturnProductAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = ReturnProductResource
    list_display = ("return_transaction_id", "JAN", "name", "price", "tax", "points")
    search_fields = ("transaction__id", "JAN__JAN", "name")


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["applicable_product_jan"].required = False
        self.fields["combo_product_jans"].required = False
        self.fields["min_quantity"].required = False


def delete_expired_coupons(modeladmin, request, queryset):
    now = timezone.now()
    if not queryset:
        queryset = Coupon.objects.all()

    expired_coupons = queryset.filter(expiration_date__lt=now)
    count = expired_coupons.count()

    if count > 0:
        expired_coupons.delete()
        modeladmin.message_user(request, f"{count} 件の有効期限切れのクーポンが削除されました。", messages.SUCCESS)
    else:
        modeladmin.message_user(request, "削除する有効期限切れのクーポンが見つかりませんでした。", messages.WARNING)


delete_expired_coupons.short_description = "有効期限を過ぎたクーポンを一括削除"


class CouponAdmin(admin.ModelAdmin):
    form = CouponForm
    list_display = (
        "code",
        "coupon_type",
        "get_applicable_product_name",
        "get_combo_products",
        "discount_value",
        "discount_percentage",
    )
    search_fields = ("code", "applicable_product_jan__name", "combo_product_jans__name")
    fields = (
        "coupon_type",
        "expiration_date",
        "discount_value",
        "discount_percentage",
        "applicable_product_jan",
        "combo_product_jans",
        "min_quantity",
    )
    readonly_fields = ("code",)
    actions = [delete_expired_coupons]

    class Media:
        js = ("admin/js/coupon_form.js",)

    def get_applicable_product_name(self, obj):
        return obj.applicable_product_jan.name if obj.applicable_product_jan else None

    get_applicable_product_name.short_description = "割引対象商品"

    def get_combo_products(self, obj):
        return ", ".join([product.name for product in obj.combo_product_jans.all()])

    get_combo_products.short_description = "組み合わせJAN"


admin.site.register(Store, StoreAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(SaleProduct, SaleProductAdmin)
admin.site.register(SaleSummary, SaleSummaryAdmin)
admin.site.register(ReturnTransaction, ReturnTransactionAdmin)
admin.site.register(ReturnProduct, ReturnProductAdmin)
admin.site.register(Coupon, CouponAdmin)
