from rest_framework import serializers
from apps.DBmaint.models import Product, Stock, Transaction, SaleProduct, ReturnProduct, ReturnTransaction, Coupon
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from sqids import Sqids
from decimal import ROUND_HALF_DOWN, ROUND_HALF_UP


# 商品のシリアライザー
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["JAN", "name", "price", "tax"]


# 在庫のシリアライザー
class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["storecode", "JAN", "quantity"]


# 販売製品のシリアライザー
class SaleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleProduct
        fields = ["JAN", "name", "price", "tax", "points"]
        read_only_fields = ["name", "price", "tax"]


# 取引のシリアライザー
class TransactionSerializer(serializers.ModelSerializer):
    sale_products = SaleProductSerializer(many=True, write_only=True)
    sale_date = serializers.DateTimeField(read_only=True)
    saleproduct_set = SaleProductSerializer(many=True, read_only=True, source="sale_products")
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "sale_type",
            "sale_id",
            "storecode",
            "staffcode",
            "deposit",
            "sale_products",
            "sale_date",
            "purchase_points",
            "tax_10_percent",
            "tax_8_percent",
            "tax_amount",
            "total_amount",
            "change",
            "saleproduct_set",
            "coupon_code",
            "discount_amount",
        ]
        read_only_fields = [
            "sale_date",
            "sale_id",
            "purchase_points",
            "tax_10_percent",
            "tax_8_percent",
            "tax_amount",
            "total_amount",
            "change",
            "saleproduct_set",
            "discount_amount",
        ]

    def validate_deposit(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("預かり金は正の値である必要があります。")
        return value

    def validate_sale_products(self, value):
        if not value:
            raise serializers.ValidationError("少なくとも1つの商品を提供する必要があります。")

        product_map = {}
        for sale_product in value:
            jan_code = sale_product.get("JAN")
            points = sale_product.get("points")

            if jan_code in product_map:
                product_map[jan_code]["points"] += points
            else:
                product_map[jan_code] = sale_product

            if points <= 0:
                raise serializers.ValidationError("ポイントは正の値である必要があります。")

            try:
                product = Product.objects.get(JAN=jan_code)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"JANコード {jan_code} を持つ商品が存在しません。")

            if product.tax not in [Decimal("10.00"), Decimal("8.00")]:
                raise serializers.ValidationError(f"JANコード {jan_code} を持つ商品の税率が無効です。")

        return list(product_map.values())

    def is_valid_coupon(self, coupon_code):
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.expiration_date < timezone.now():
                return False
            return True
        except Coupon.DoesNotExist:
            return False

    def validate_coupon_code(self, value):
        if value and not self.is_valid_coupon(value):
            raise serializers.ValidationError("無効または期限切れのクーポンコードです。")
        return value

    def apply_discount(self, amount, coupon, sale_products_data):
        discount = 0

        if coupon.coupon_type == "percent":
            discount = (amount * coupon.discount_percentage / Decimal("100.0")).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        elif coupon.coupon_type == "amount":
            discount = coupon.discount_value
        elif coupon.coupon_type == "product":
            applicable_products = coupon.applicable_product_jan
            for sale_product in sale_products_data:
                if str(sale_product["JAN"]) == applicable_products.JAN:
                    discount = coupon.discount_value
                    break
        elif coupon.coupon_type == "combo":
            combo_products = coupon.combo_product_jans.all()
            combo_jan_list = [product.JAN for product in combo_products]
            sale_jan_list = [str(product["JAN"]) for product in sale_products_data]
            if all(jan in sale_jan_list for jan in combo_jan_list):
                discount = int(coupon.discount_value)
        elif coupon.coupon_type == "multi":
            applicable_product_jan = coupon.applicable_product_jan
            total_quantity = sum(
                [
                    product["points"]
                    for product in sale_products_data
                    if str(product["JAN"]) == applicable_product_jan.JAN
                ]
            )
            if total_quantity >= coupon.min_quantity:
                discount_multiplier = total_quantity // coupon.min_quantity
                discount = coupon.discount_value * discount_multiplier
        return amount - discount, discount

    def create_transaction_instance(self, validated_data, sale_id, current_time):
        return Transaction.objects.create(
            sale_date=current_time,
            sale_id=sale_id,
            purchase_points=0,
            tax_10_percent=Decimal("0.00"),
            tax_8_percent=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("0.00"),
            change=Decimal("0.00"),
            **validated_data,
        )

    def process_sale_product(self, sale_product_data, storecode, transaction_instance):
        jan_code = sale_product_data["JAN"]
        points = sale_product_data["points"]

        try:
            product = Product.objects.get(JAN=jan_code)
        except Product.DoesNotExist:
            raise serializers.ValidationError(f"JANコード {jan_code} を持つ商品が存在しません。")

        price = product.price
        tax_rate = product.tax  # `tax_rate`を取得

        try:
            stock = Stock.objects.get(storecode=storecode, JAN=product)
        except Stock.DoesNotExist:
            raise serializers.ValidationError(f"店舗コード {storecode} と JANコード {jan_code} の在庫が存在しません。")

        stock.quantity -= points
        stock.save()

        # `SaleProduct`オブジェクトを作成
        SaleProduct.objects.create(
            transaction=transaction_instance,
            JAN=product,
            name=product.name,
            price=price,
            tax=tax_rate,  # `tax_rate`を保存
            points=points,
        )

        # `tax_rate`をsale_product_dataに追加
        sale_product_data["price"] = price
        sale_product_data["tax"] = tax_rate

        return price, tax_rate, points  # `tax_rate`を返す

    def calculate_tax_amounts(self, tax_10_total_price, tax_8_total_price):
        tax_10_total = (tax_10_total_price * Decimal("10.00") / Decimal("110.00")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_DOWN
        )
        tax_8_total = (tax_8_total_price * Decimal("8.00") / Decimal("108.00")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_DOWN
        )
        return tax_10_total, tax_8_total

    def create(self, validated_data):
        sale_products_data = validated_data.pop("sale_products")
        storecode = validated_data.get("storecode")
        deposit = validated_data.get("deposit")
        coupon_code = validated_data.get("coupon_code")

        purchase_points = 0
        tax_10_total_price = Decimal("0.00")
        tax_8_total_price = Decimal("0.00")

        with transaction.atomic():
            current_time = timezone.now()
            storecode_str = str(storecode)
            staffcode = str(validated_data.get("staffcode"))
            cutted_ms = str(current_time).split(".")[1][:4]
            sqids = Sqids(min_length=10, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            sale_id = sqids.encode([int(cutted_ms), int(storecode_str), int(staffcode)])

            transaction_instance = Transaction.objects.create(
                **validated_data,
                sale_id=sale_id,
                sale_date=current_time,
                purchase_points=0,
                tax_10_percent=Decimal("0.00"),
                tax_8_percent=Decimal("0.00"),
                tax_amount=Decimal("0.00"),
                total_amount=Decimal("0.00"),
                change=Decimal("0.00"),
                discount_amount=Decimal("0.00"),
            )

            for sale_product_data in sale_products_data:
                price, tax_rate, points = self.process_sale_product(sale_product_data, storecode, transaction_instance)
                purchase_points += points

                if tax_rate == Decimal("10.00"):
                    tax_10_total_price += price * points
                elif tax_rate == Decimal("8.00"):
                    tax_8_total_price += price * points

            total_amount_with_tax = tax_10_total_price + tax_8_total_price
            discount_amount = Decimal("0.00")

            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    total_amount_with_tax, discount_amount = self.apply_discount(
                        total_amount_with_tax, coupon, sale_products_data
                    )
                except Coupon.DoesNotExist:
                    raise serializers.ValidationError("無効または期限切れのクーポンコードです。")

                if coupon.coupon_type in ["percent", "amount", "combo"]:
                    tax_10_total_price -= discount_amount * (tax_10_total_price / total_amount_with_tax)
                    tax_8_total_price -= discount_amount * (tax_8_total_price / total_amount_with_tax)
                elif coupon.coupon_type in ["product", "multi"]:
                    tax_10_total_price = sum(
                        p["price"] * p["points"] for p in sale_products_data if Decimal(p["tax"]) == Decimal("10.00")
                    ) or 0
                    tax_8_total_price = sum(
                        p["price"] * p["points"] for p in sale_products_data if Decimal(p["tax"]) == Decimal("8.00")
                    ) or 0

            tax_10_total, tax_8_total = self.calculate_tax_amounts(tax_10_total_price, tax_8_total_price)
            tax_amount = tax_10_total + tax_8_total

            change = deposit - total_amount_with_tax

            if deposit < total_amount_with_tax:
                raise serializers.ValidationError("預かり金は総額を超えている必要があります。")
            if change < Decimal("0.00"):
                raise serializers.ValidationError("お釣りは正の値である必要があります。")

            transaction_instance.purchase_points = purchase_points
            transaction_instance.coupon_code = coupon_code
            transaction_instance.tax_10_percent = tax_10_total
            transaction_instance.tax_8_percent = tax_8_total
            transaction_instance.tax_amount = tax_amount
            transaction_instance.total_amount = total_amount_with_tax
            transaction_instance.change = change
            transaction_instance.discount_amount = discount_amount

            transaction_instance.save()

        return transaction_instance


# 返品製品のシリアライザー
class ReturnProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProduct
        fields = ["JAN", "name", "price", "tax", "points"]
        read_only_fields = ["name", "price", "tax"]

    def validate_points(self, value):
        if value == 0:
            raise serializers.ValidationError("Points must not be zero.")
        return value


# 返品取引のシリアライザー
class ReturnTransactionSerializer(serializers.ModelSerializer):
    return_products = ReturnProductSerializer(many=True, write_only=True, required=False)
    return_date = serializers.DateTimeField(read_only=True)
    returnproduct_set = ReturnProductSerializer(many=True, read_only=True, source='return_products')

    class Meta:
        model = ReturnTransaction
        fields = [
            "return_type", "return_id", "originSaleid", "storecode", "staffcode",
            "reason", "return_points", "tax_10_percent", "tax_8_percent",
            "tax_amount", "return_amount", "return_date", "return_products", "returnproduct_set"
        ]
        read_only_fields = [
            "return_id", "storecode", "return_points", "tax_10_percent", "tax_8_percent",
            "tax_amount", "return_amount", "return_date", "returnproduct_set"
        ]

    def validate_originSaleid(self, value):
        if not Transaction.objects.filter(sale_id=value.sale_id, sale_type__in=[1, 4]).exists():
            raise serializers.ValidationError("The relevant transaction does not exist or is not a returnable transaction.")
        return value

    def validate(self, data):
        return_type = data.get('return_type')
        return_products = data.get('return_products', [])
        originSaleid = data.get('originSaleid')

        if return_type == '1':  # 全返品の場合
            if not originSaleid:
                raise serializers.ValidationError("Origin Sale ID must be provided for full return.")
            sale_products = SaleProduct.objects.filter(transaction=originSaleid)
            if not sale_products.exists():
                raise serializers.ValidationError("No products found for the given sale transaction.")
            data['return_products'] = [
                {'JAN': sp.JAN.JAN, 'name': sp.name, 'price': sp.price, 'tax': sp.tax, 'points': sp.points}
                for sp in sale_products
            ]
        else:  # 一部返品の場合
            if not return_products:
                raise serializers.ValidationError("At least one return product must be provided.")
            sale_products = SaleProduct.objects.filter(transaction=originSaleid)
            sale_product_jans = sale_products.values_list('JAN', flat=True)
            for return_product in return_products:
                if return_product['JAN'] not in sale_product_jans:
                    raise serializers.ValidationError(f"Product with JAN {return_product['JAN']} is not part of the original transaction.")
        
        return data

    def apply_discount(self, amount, coupon, sale_products_data):
        discount = 0
        
        if coupon.coupon_type == "percent":
            discount = (amount * coupon.discount_percentage / Decimal("100.0")).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        elif coupon.coupon_type == "amount":
            discount = coupon.discount_value
        elif coupon.coupon_type == "product":
            applicable_products = coupon.applicable_product_jan
            for sale_product in sale_products_data:
                if str(sale_product["JAN"]) == applicable_products.JAN:
                    discount = coupon.discount_value
                    break
        elif coupon.coupon_type == "combo":
            combo_products = coupon.combo_product_jans.all()
            combo_jan_list = [product.JAN for product in combo_products]
            sale_jan_list = [str(product["JAN"]) for product in sale_products_data]
            if all(jan in sale_jan_list for jan in combo_jan_list):
                discount = int(coupon.discount_value)
        elif coupon.coupon_type == "multi":
            applicable_product_jan = coupon.applicable_product_jan
            total_quantity = sum([product["points"] for product in sale_products_data if str(product["JAN"]) == applicable_product_jan.JAN])
            if total_quantity >= coupon.min_quantity:
                discount_multiplier = total_quantity // coupon.min_quantity
                discount = coupon.discount_value * discount_multiplier
        return amount - discount, discount

    def calculate_tax_amounts(self, tax_10_total_price, tax_8_total_price):
        tax_10_total = (tax_10_total_price * Decimal("10.00") / Decimal("110.00")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_DOWN
        )
        tax_8_total = (tax_8_total_price * Decimal("8.00") / Decimal("108.00")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_DOWN
        )
        return tax_10_total, tax_8_total

    def create(self, validated_data):
        return_products_data = validated_data.pop("return_products")
        origin_sale_id = validated_data.get("originSaleid")
        storecode = origin_sale_id.storecode

        return_points = 0
        tax_10_total_price = Decimal("0.00")
        tax_8_total_price = Decimal("0.00")

        with transaction.atomic():
            current_time = timezone.now()
            storecode_str = str(storecode)
            staffcode = str(validated_data.get("staffcode"))
            cutted_ms = str(current_time).split('.')[1][:4]
            sqids = Sqids(min_length=10, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            return_id = sqids.encode([int(cutted_ms), int(storecode_str), int(staffcode)])
            return_instance = ReturnTransaction.objects.create(
                return_date=current_time,
                return_id=return_id,
                return_points=0,
                tax_10_percent=Decimal("0.00"),
                tax_8_percent=Decimal("0.00"),
                tax_amount=Decimal("0.00"),
                return_amount=Decimal("0.00"),
                storecode=storecode,
                **validated_data
            )

            for return_product_data in return_products_data:
                jan_code = return_product_data["JAN"]
                points = return_product_data["points"]

                try:
                    product = Product.objects.get(JAN=jan_code)
                except Product.DoesNotExist:
                    raise serializers.ValidationError(f"Product with JAN code {jan_code} does not exist.")

                price = product.price
                tax_rate = product.tax

                if tax_rate == Decimal("10.00"):
                    tax_10_total_price += price * points
                elif tax_rate == Decimal("8.00"):
                    tax_8_total_price += price * points

                try:
                    stock = Stock.objects.get(storecode=storecode, JAN=product)
                except Stock.DoesNotExist:
                    raise serializers.ValidationError(f"Stock for product with JAN code {jan_code} in store {storecode} does not exist.")

                stock.quantity += points
                stock.save()

                ReturnProduct.objects.create(
                    return_transaction=return_instance, JAN=product, name=product.name, price=price, tax=tax_rate, points=points
                )

                return_points += points

            tax_10_total, tax_8_total = self.calculate_tax_amounts(tax_10_total_price, tax_8_total_price)
            tax_amount = tax_10_total + tax_8_total
            return_amount_with_tax = tax_10_total_price + tax_8_total_price

            # 割引の適用
            discount_amount = origin_sale_id.discount_amount
            if discount_amount:
                return_amount_with_tax -= discount_amount

            return_instance.return_points = return_points
            return_instance.tax_10_percent = tax_10_total
            return_instance.tax_8_percent = tax_8_total
            return_instance.tax_amount = tax_amount
            return_instance.return_amount = return_amount_with_tax + tax_amount
            return_instance.save()

            # Origin transaction sale_type update
            origin_sale_id.sale_type = 2
            origin_sale_id.save()

        return return_instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["returnproduct_set"] = ReturnProductSerializer(instance.return_products.all(), many=True).data
        return representation
