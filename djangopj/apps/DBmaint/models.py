from django.db import models
from apps.user.models import CustomUser
from django.core.exceptions import ValidationError
from .utils import is_valid_jan_code, is_valid_tax
from simple_history.models import HistoricalRecords
import random, string
from django.db.models import UniqueConstraint


class Store(models.Model):
    storecode = models.CharField(max_length=255, unique=True, verbose_name="店番")
    name = models.CharField(max_length=255, verbose_name="店舗名")

    def __str__(self):
        return self.storecode

    class Meta:
        verbose_name = "店舗マスター"
        verbose_name_plural = "店舗マスター"


class Product(models.Model):
    JAN = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, verbose_name="商品名")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="価格")
    tax = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="税率")

    def clean(self):
        if not is_valid_jan_code(self.JAN):
            raise ValidationError({"JAN": "無効なJANコードです。"})
        if not is_valid_tax(self.tax):
            raise ValidationError({"tax": "無効な税率です。"})

    def __str__(self):
        return self.JAN

    class Meta:
        verbose_name = "商品マスター"
        verbose_name_plural = "商品マスター"


class Stock(models.Model):
    storecode = models.ForeignKey(Store, on_delete=models.CASCADE, to_field="storecode", verbose_name="店番")  # 店舗コード
    JAN = models.ForeignKey(Product, on_delete=models.CASCADE, to_field="JAN")
    quantity = models.IntegerField(verbose_name="在庫数")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "在庫マスター"
        verbose_name_plural = "在庫マスター"
        # storecodeとJANの組み合わせがユニークであることを保証
        # これがないと在庫が再生成できなくなる
        constraints = [
            UniqueConstraint(fields=['storecode', 'JAN'], name='unique_storecode_jan')
        ]


class Transaction(models.Model):
    SALE_TYPES = (
        ("1", "販売"),
        ("2", "返品"),
        ("3", "Void"),
        ("4", "取引変更"),
    )
    sale_type = models.CharField(max_length=1, choices=SALE_TYPES, default="1")
    sale_id = models.CharField(max_length=255, unique=True)
    sale_date = models.DateTimeField()
    storecode = models.ForeignKey(
        Store, null=True, on_delete=models.DO_NOTHING, to_field="storecode"
    )  # 店舗コード storeに基づく
    staffcode = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, to_field="staffcode")
    purchase_points = models.IntegerField()
    # SaleProductのJANをキーにProductテーブルを検索し、taxが10%のものの合計金額を計算 10%商品の（price * tax * points）の合計
    coupon_code = models.CharField(blank=True, null=True, max_length=13)
    tax_10_percent = models.IntegerField()
    # SaleProductのJANをキーにProductテーブルを検索し、taxが8%のものの合計金額を計算 8%商品の（price * tax * points）の合計
    tax_8_percent = models.IntegerField()
    tax_amount = models.IntegerField()
    total_amount = models.IntegerField()
    discount_amount = models.IntegerField(default=0)
    deposit = models.IntegerField()
    change = models.IntegerField()
    history = HistoricalRecords()

    def __str__(self):
        return self.sale_id

    class Meta:
        verbose_name = "取引履歴"
        verbose_name_plural = "取引履歴"


class SaleProduct(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="sale_products")
    JAN = models.ForeignKey(Product, on_delete=models.DO_NOTHING, to_field="JAN")
    name = models.CharField(
        max_length=255
    )  # 商品名 Productsから取得した情報をここに保存する 非正規形となっているのは販売時の商品名を保存するため
    # 商品価格(税込) 取得したデータはすでに税込金額のため再計算の必要はない  Productsから取得したpriceをここに保存する 販売時の価格を保存するため非正規形となっている
    price = models.IntegerField()
    tax = models.IntegerField()
    points = models.IntegerField()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "販売商品詳細"
        verbose_name_plural = "販売商品詳細"


COUPON_TYPE_CODES = {
    "product": "01",
    "combo": "02",
    "multi": "03",
    "amount": "04",
    "percent": "05",
}


def calculate_check_digit(code):
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(code)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return (10 - (checksum % 10)) % 10


def generate_unique_identifier():
    return "".join(random.choices(string.digits, k=6))


def generate_coupon_code(coupon_type):
    prefix = "28"
    type_code = COUPON_TYPE_CODES.get(coupon_type, "00")
    unique_identifier = generate_unique_identifier()
    partial_code = prefix + type_code + unique_identifier
    check_digit = calculate_check_digit(partial_code)
    return partial_code + str(check_digit)


class Coupon(models.Model):
    COUPON_TYPES = [
        ("product", "商品指定割引"),
        ("combo", "同時購入割引"),
        ("multi", "複数点購入割引"),
        ("amount", "小計金額割引"),
        ("percent", "小計割合割引"),
    ]

    code = models.CharField(max_length=13, primary_key=True, unique=True, blank=True, verbose_name="クーポンコード")
    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPES, verbose_name="クーポン種別")
    expiration_date = models.DateTimeField(verbose_name="有効期限")
    discount_value = models.IntegerField(verbose_name="割引金額")
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="割引割合(%)"
    )
    applicable_product_jan = models.ForeignKey(
        "Product",
        related_name="applicable_coupons",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="割引対象商品",
    )
    combo_product_jans = models.ManyToManyField(
        "Product", related_name="combo_coupons", blank=True, verbose_name="組み合わせJAN"
    )
    min_quantity = models.PositiveIntegerField(default=1, verbose_name="最低購入数")

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_coupon_code(self.coupon_type)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "クーポンマスター"
        verbose_name_plural = "クーポンマスター"


class ReturnTransaction(models.Model):
    RETURN_TYPES = (
        ("1", "全返品"),
        ("2", "一部返品"),
        ("3", "Void"),
        ("4", "取引変更"),
    )
    REASON = (
        ("1", "お客様都合"),
        ("2", "弊社都合"),
    )
    return_type = models.CharField(max_length=1, choices=RETURN_TYPES)
    originSaleid = models.ForeignKey(Transaction, on_delete=models.DO_NOTHING, to_field="sale_id")
    return_id = models.CharField(max_length=255, unique=True)
    return_date = models.DateTimeField()
    storecode = models.ForeignKey(Store, null=True, on_delete=models.DO_NOTHING, )
    staffcode = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, to_field="staffcode")
    reason = models.CharField(max_length=1, choices=REASON)
    return_points = models.IntegerField()
    tax_10_percent = models.IntegerField()
    tax_8_percent = models.IntegerField()
    tax_amount = models.IntegerField()
    return_amount = models.IntegerField()

    def __str__(self):
        return self.return_id

    class Meta:
        verbose_name = "返品商品詳細"
        verbose_name_plural = "返品商品詳細"


class ReturnProduct(models.Model):
    return_transaction = models.ForeignKey(ReturnTransaction, on_delete=models.CASCADE, related_name="return_products")
    JAN = models.ForeignKey(Product, on_delete=models.DO_NOTHING, to_field="JAN")
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    tax = models.IntegerField()
    points = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "返品履歴"
        verbose_name_plural = "返品履歴"


class SaleSummary(Transaction):
    class Meta:
        proxy = True
        verbose_name = "販売概要"
        verbose_name_plural = "販売概要"
